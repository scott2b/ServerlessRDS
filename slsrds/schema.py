from pprint import pprint
import psycopg2
import psycopg2.extras
from prettytable import PrettyTable
from .config import get_config


COLUMNS = {
    'column_name': 'name',
    'data_type': 'type',
    'character_maximum_length': 'maxlen',
    'is_nullable': 'null',
    'numeric_precision': 'prec',
    'numeric_precision_radix': 'radix',
    'numeric_scale': 'scale'
}


def fix_type(t):
    if t == 'timestamp without time zone':
        t = 'ts (no tz)'
    return t


def get_schema(event, context):
    identifier = event.get('db', 'default')
    config = get_config()
    try:
        database = config[f'database.{identifier}']
        if database.get('name') is None or database.get('user') is None:
            raise Exception(f'Database not configured: {identifier}')
    except KeyError:
        raise Exception(f'Database not configured: {identifier}')
    db = psycopg2.connect(
        dbname=database['name'],
        user=database['user'],
        password=database.get('password'),
        host=database.get('host')
    )
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = "SELECT table_name FROM information_schema.tables WHERE " \
        "table_schema='public' AND table_type='BASE TABLE'"
    cursor.execute(query)
    tables = (x['table_name'] for x in cursor.fetchall())
    response = {}
    for tbl in tables:
        print(tbl.capitalize())
        cursor.execute("""SELECT column_name, data_type,
            character_maximum_length,
            numeric_precision, numeric_precision_radix,
            numeric_scale, is_nullable
            FROM information_schema.columns
            WHERE table_name=%s
            ORDER BY ordinal_position""", (tbl, ))
        r = cursor.fetchall()
        response[tbl] = r
        t = PrettyTable()
        field_names = [
            'column_name',
            'data_type',
            'character_maximum_length',
            'is_nullable',
            'numeric_precision',
            'numeric_precision_radix',
            'numeric_scale']
        t.field_names = [COLUMNS[f] for f in field_names]
        for row in r:
            row['data_type'] = fix_type(row['data_type'])
            t.add_row([row[f] or '' for f in field_names])
        print(t)
    cursor.close()
    db.close()
    return response


if __name__=='__main__':
    get_schema('default')
