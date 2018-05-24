# pg-batch

[![Build Status](https://travis-ci.org/gabfl/pg-batch.svg?branch=master)](https://travis-ci.org/gabfl/pg-batch)

PostgreSQL equivalent of https://github.com/gabfl/mysql-batch.

Updating or deleting a large amount of rows in PostgreSQL will create locks that will paralyze other queries running in parallel.

This tool will run UPDATE and DELETE queries in small batches to limit locking. If a large number of rows has to be updated or deleted, it is also possible to limit the number of rows selected at once.

## Installation

```
pip3 install pg_batch
```

## UPDATE example

You can run this example with the schema available in [sample_table/schema.sql](sample_table/schema.sql)

The following example will be identical to the following update:

```sql
UPDATE batch_test SET date = NOW() WHERE number > 30 AND date is NULL;
```

This is the equivalent to process this update with batches of 20 rows:

```bash
pg_batch --host localhost \
         --user postgres \
         --password secret_password \
         --database "test" \
         --table "batch_test" \
         --write_batch_size 20 \
         --where "number > 30 AND date IS NULL" \
         --set "date = NOW()"
```

Output sample:

```bash
* Selecting data...
   query: SELECT id as id FROM batch_test WHERE number > 30 AND date IS NULL AND id > 0 ORDER BY id LIMIT 10000
* Preparing to modify 70 rows...
* Updating 20 rows...
   query: UPDATE batch_test SET date = NOW() WHERE id IN (31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50)
* Start updating? [Y/n]
* Updating 20 rows...
   query: UPDATE batch_test SET date = NOW() WHERE id IN (51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70)
* Updating 20 rows...
   query: UPDATE batch_test SET date = NOW() WHERE id IN (71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90)
* Updating 10 rows...
   query: UPDATE batch_test SET date = NOW() WHERE id IN (91, 92, 93, 94, 95, 96, 97, 98, 99, 100)
* Selecting data...
   query: SELECT id as id FROM batch_test WHERE number > 30 AND date IS NULL AND id > 100 ORDER BY id LIMIT 10000
* No more rows to modify!
* Program exited
```

## DELETE example

The following example will be identical to the following delete:

```sql
DELETE FROM batch_test WHERE number > 30 AND date is NULL;
```

This is the equivalent to process this delete with batches of 20 rows:

```bash
pg_batch --host localhost \
         --user postgres \
         --password secret_password \
         --database "test" \
         --table "batch_test" \
         --write_batch_size 20 \
         --where "number > 30 AND date IS NULL" \
         --action "delete"
```

Output sample:

```bash
* Selecting data...
   query: SELECT id as id FROM batch_test WHERE number > 30 AND date IS NULL AND id > 0 ORDER BY id LIMIT 10000
* Preparing to modify 70 rows...
* Deleting 20 rows...
   query: DELETE FROM batch_test WHERE id IN (31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50)
* Start deleting? [Y/n]
* Deleting 20 rows...
   query: DELETE FROM batch_test WHERE id IN (51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70)
* Deleting 20 rows...
   query: DELETE FROM batch_test WHERE id IN (71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90)
* Deleting 10 rows...
   query: DELETE FROM batch_test WHERE id IN (91, 92, 93, 94, 95, 96, 97, 98, 99, 100)
* Selecting data...
   query: SELECT id as id FROM batch_test WHERE number > 30 AND date IS NULL AND id > 100 ORDER BY id LIMIT 10000
* No more rows to modify!
* Program exited
```

## Usage

```bash
usage: pg_batch [-h] [-H HOST] [-P PORT] -U USER [-p PASSWORD] -d DATABASE -t
                TABLE [-id PRIMARY_KEY] -w WHERE [-s SET]
                [-rbz READ_BATCH_SIZE] [-wbz WRITE_BATCH_SIZE] [-S SLEEP]
                [-a {update,delete}] [-n]

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  PostgreSQL server host
  -P PORT, --port PORT  PostgreSQL server port
  -U USER, --user USER  PostgreSQL user
  -p PASSWORD, --password PASSWORD
                        PostgreSQL password
  -d DATABASE, --database DATABASE
                        PostgreSQL database name
  -t TABLE, --table TABLE
                        PostgreSQL table
  -id PRIMARY_KEY, --primary_key PRIMARY_KEY
                        Name of the primary key column
  -w WHERE, --where WHERE
                        Select WHERE clause
  -s SET, --set SET     Update SET clause
  -rbz READ_BATCH_SIZE, --read_batch_size READ_BATCH_SIZE
                        Select batch size
  -wbz WRITE_BATCH_SIZE, --write_batch_size WRITE_BATCH_SIZE
                        Update/delete batch size
  -S SLEEP, --sleep SLEEP
                        Sleep after each batch
  -a {update,delete}, --action {update,delete}
                        Action ('update' or 'delete')
  -n, --no_confirm      Don't ask for confirmation before to run the write
                        queries
```

## License

This program is under MIT license ([view license](LICENSE)).
