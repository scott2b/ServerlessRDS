import psycopg2
from .config import get_config

"""
WARNING: This will drop your database. Use with caution
"""

def drop_db(event, context):
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
        if db_cfg.get('name') is None:
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
    query = f"DROP DATABASE {db_cfg['name']};"
    cursor.execute(query);
    cursor.close()
    admin_db.close()
