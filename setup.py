from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup (
    name = 'pg_batch',
    version = '1.0.3',
    description = 'Run large PostgreSQL UPDATE and DELETE queries with small batches to prevent locks',
    long_description = long_description,
    author = 'Gabriel Bordeaux',
    author_email = 'pypi@gab.lc',
    url = 'https://github.com/gabfl/pg-batch',
    license = 'MIT',
    packages = ['pg_batch'],
    install_requires = ['psycopg2', 'argparse'], # external dependencies
    entry_points = {
        'console_scripts': [
            'pg_batch = pg_batch.pg_batch:main',
        ],
    },
)
