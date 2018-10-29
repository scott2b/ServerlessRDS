import psycopg2
from .config import get_config

"""
Note: dblink extension is required. If you get something like:

psycopg2.ProgrammingError: function dblink_exec(text, unknown) does not exist

You need to run:
CREATE EXTENSION dblink;

Alternatively, on a given schema:
CREATE EXTENSION dblink SCHEMA extensions;
"""

def create_db(event, context):
    identifier = event.get('db', 'default')
    config = get_config()
    try:
        admin_cfg = config[f'database.admin']
        if admin_cfg.get('name') is None or admin_cfg.get('user') is None:
            raise Exception('admin database is not configured properly')
    except KeyError:
        raise Exception('admin database is not configured')
    try:
        db_cfg = config[f'database.{identifier}']
        if db_cfg.get('name') is None or db_cfg.get('user') is None:
            raise Exception(f'Database not configured properly: {identifier}')
    except KeyError:
        raise Exception(f'Database not configured: {identifier}')
    admin_db = psycopg2.connect(
        dbname=admin_cfg['name'],
        user=admin_cfg['user'],
        password=admin_cfg.get('password'),
        host=admin_cfg.get('host')
    )
    admin_db.autocommit = True
    cursor = admin_db.cursor()
    query = f"""
DO
$do$
BEGIN
   IF EXISTS (SELECT 1 FROM pg_database WHERE datname = '{db_cfg['name']}') THEN
      RAISE NOTICE 'Database already exists';
   ELSE
      PERFORM dblink_exec('dbname=' || current_database()  -- current db
                        , 'CREATE DATABASE {db_cfg['name']}');
   END IF;
END
$do$;
"""
    cursor.execute(query);
    query = f"""
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT
      FROM   pg_catalog.pg_roles
      WHERE  rolname = '{db_cfg['user']}') THEN
      CREATE ROLE {db_cfg['user']} LOGIN PASSWORD '{db_cfg.get('password','')}';
   END IF;
END
$do$;
"""
    cursor.execute(query)
    cursor.execute(f"""
GRANT ALL PRIVILEGES ON DATABASE {db_cfg['name']} to {db_cfg['user']};
    """)
    cursor.close()
    admin_db.close()
