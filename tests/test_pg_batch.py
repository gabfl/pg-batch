import os
import sys
import unittest
from unittest.mock import patch

import psycopg2

from pg_batch import pg_batch


class Test(unittest.TestCase):

    # Connection settings can be overridden through the standard libpq env vars
    host = os.environ.get('PGHOST', 'localhost')
    user = os.environ.get('PGUSER', 'db_user')
    database = os.environ.get('PGDATABASE', 'my_db')
    password = os.environ.get('PGPASSWORD', 'db_password')
    port = int(os.environ.get('PGPORT', 5432))

    # Sample schema
    schema_path = os.path.join(os.path.dirname(__file__), '..',
                               'sample_table', 'schema.sql')

    def setUp(self):
        # Read sample schema
        with open(self.schema_path, 'r') as f:
            schema = f.read()

        # Apply schema for test
        self.db = self.connect()
        with self.db.cursor() as cursor:
            cursor.execute(schema)
        self.db.commit()

        # Connection used by pg_batch's module-level helpers
        pg_batch.connection = self.connect()
        pg_batch.confirmed_write = True

    def tearDown(self):
        if not pg_batch.connection.closed:
            pg_batch.connection.close()
        self.db.close()

    def connect(self):
        return pg_batch.connect(
            self.host, self.user, self.port, self.password, self.database)

    def scalar(self, sql):
        """ Run a query and return the first column of the first row """
        self.db.rollback()  # make sure we see the latest committed data
        with self.db.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchone()[0]

    def count(self, where='TRUE'):
        return self.scalar('SELECT COUNT(*) FROM batch_test WHERE ' + where)

    def execute(self, **kwargs):
        params = dict(host=self.host, user=self.user, port=self.port,
                      password=self.password, database=self.database,
                      table='batch_test')
        params.update(kwargs)
        return pg_batch.execute(**params)

    def test_update_batch(self):
        self.assertTrue(pg_batch.update_batch(
            [4, 5, 6], 'batch_test', 'date=NOW()'))

        self.assertEqual(self.count('date IS NOT NULL'), 3)
        self.assertEqual(self.count('id IN (4, 5, 6) AND date IS NOT NULL'), 3)

    def test_update_batch_custom_primary_key(self):
        self.assertTrue(pg_batch.update_batch(
            [10, 20], 'batch_test', 'date=NOW()', primary_key='number'))

        self.assertEqual(
            self.count('number IN (10, 20) AND date IS NOT NULL'), 2)

    def test_update_batch_2(self):
        # Return should be none if there are no `ids`
        self.assertIsNone(pg_batch.update_batch(
            [], 'batch_test', 'date=NOW()'))

    def test_update_batch_3(self):
        pg_batch.confirmed_write = False

        # Should exit if the client refuses the update
        with patch('builtins.input', return_value='no'):
            self.assertRaises(SystemExit, pg_batch.update_batch,
                              [1, 2, 3], 'batch_test', 'date=NOW()')

        self.assertEqual(self.count('date IS NOT NULL'), 0)

    def test_update_batch_confirm(self):
        pg_batch.confirmed_write = False

        # Accepting the first prompt runs the query and skips future prompts
        with patch('builtins.input', return_value='y'):
            self.assertTrue(pg_batch.update_batch(
                [1, 2, 3], 'batch_test', 'date=NOW()'))

        self.assertTrue(pg_batch.confirmed_write)
        self.assertEqual(self.count('date IS NOT NULL'), 3)

    def test_delete_batch(self):
        self.assertTrue(pg_batch.delete_batch([1, 2, 3], 'batch_test'))

        self.assertEqual(self.count(), 997)
        self.assertEqual(self.count('id IN (1, 2, 3)'), 0)

    def test_delete_batch_2(self):
        # Return should be none if there are no `ids`
        self.assertIsNone(pg_batch.delete_batch([], 'batch_test'))

    def test_delete_batch_3(self):
        pg_batch.confirmed_write = False

        # Should exit if the client refuses the delete
        with patch('builtins.input', return_value='no'):
            self.assertRaises(SystemExit, pg_batch.delete_batch,
                              [1, 2, 3], 'batch_test')

        self.assertEqual(self.count(), 1000)

    def test_run_query(self):
        self.assertTrue(pg_batch.run_query('SELECT 1'))

        with patch('time.sleep') as sleep:
            self.assertTrue(pg_batch.run_query('SELECT 1', 0.001))
            sleep.assert_called_once_with(0.001)

    def test_get_input(self):
        with patch('builtins.input', return_value='yes'):
            self.assertEqual(pg_batch.get_input(), 'yes')

        with patch('builtins.input', return_value='NO'):
            self.assertEqual(pg_batch.get_input(), 'no')

    def test_query_yes_no(self):
        with patch('builtins.input', return_value='yes'):
            self.assertTrue(pg_batch.query_yes_no('some question?'))

        with patch('builtins.input', return_value='yes'):
            self.assertTrue(pg_batch.query_yes_no('some question?', None))

        with patch('builtins.input', return_value='yes'):
            self.assertTrue(pg_batch.query_yes_no('some question?', 'no'))

        with patch('builtins.input', return_value='no'):
            self.assertFalse(pg_batch.query_yes_no('some question?'))

        # Test invalid default
        self.assertRaises(ValueError, pg_batch.query_yes_no,
                          'unknown_engine', 'invalid_value')

        # Test empty input with a default value
        with patch('builtins.input', return_value=''):
            self.assertTrue(pg_batch.query_yes_no('some question?', 'yes'))
        with patch('builtins.input', return_value=''):
            self.assertFalse(pg_batch.query_yes_no('some question?', 'no'))

    def test_query_yes_no_invalid_answer(self):
        # An invalid answer asks the question again
        with patch('builtins.input', side_effect=['maybe', 'n']) as input_:
            self.assertFalse(pg_batch.query_yes_no('some question?'))
            self.assertEqual(input_.call_count, 2)

    def test_connect(self):
        connection = self.connect()
        self.assertIsInstance(connection, psycopg2.extensions.connection)
        connection.close()

    def test_connect_2(self):
        # Test exception for connection error
        self.assertRaises(RuntimeError, pg_batch.connect,
                          self.host, 'invalid_value', self.port, self.password, self.database)

    def test_execute(self):
        self.assertTrue(self.execute(action='update',
                                     where='date IS NULL',
                                     set_='date=NOW()',
                                     no_confirm=True,
                                     read_batch_size=35,
                                     write_batch_size=15))

        self.assertEqual(self.count('date IS NULL'), 0)

    def test_execute_2(self):
        with patch('builtins.input', return_value='yes') as input_:
            self.assertTrue(self.execute(action='update',
                                         where='date IS NULL',
                                         set_='date=NOW()',
                                         read_batch_size=35,
                                         write_batch_size=15))

            # Confirmation is only asked once
            input_.assert_called_once()

        self.assertEqual(self.count('date IS NULL'), 0)

    def test_execute_3(self):
        self.assertTrue(self.execute(action='delete',
                                     where='date IS NULL',
                                     no_confirm=True,
                                     read_batch_size=35,
                                     write_batch_size=18))

        self.assertEqual(self.count(), 0)

    def test_execute_partial_where(self):
        # Only rows matching the WHERE clause are modified
        self.assertTrue(self.execute(action='delete',
                                     where='number > 30',
                                     no_confirm=True,
                                     write_batch_size=20))

        self.assertEqual(self.count(), 30)
        self.assertEqual(self.scalar('SELECT MAX(number) FROM batch_test'), 30)

    def test_execute_declined(self):
        with patch('builtins.input', return_value='n'):
            self.assertTrue(self.execute(action='delete',
                                         where='TRUE',
                                         write_batch_size=10))

        self.assertEqual(self.count(), 1000)

    def test_execute_4(self):
        # Test exception for update without a set
        self.assertRaises(RuntimeError, self.execute,
                          action='update',
                          where='date IS NULL',
                          no_confirm=True)

    def test_main(self):
        argv = ['pg_batch',
                '--host', self.host,
                '--port', str(self.port),
                '--user', self.user,
                '--password', self.password,
                '--database', self.database,
                '--table', 'batch_test',
                '--where', 'number <= 100',
                '--set', 'date = NOW()',
                '--write_batch_size', '20',
                '--read_batch_size', '50',
                '--no_confirm']
        with patch.object(sys, 'argv', argv):
            pg_batch.main()

        self.assertEqual(self.count('date IS NOT NULL'), 100)
        self.assertEqual(self.count('number > 100 AND date IS NOT NULL'), 0)

    def test_main_missing_required_args(self):
        with patch.object(sys, 'argv', ['pg_batch', '--user', 'x']):
            with patch('sys.stderr'):
                self.assertRaises(SystemExit, pg_batch.main)


if __name__ == '__main__':
    unittest.main()
