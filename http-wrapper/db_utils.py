''' Utility functions for interfacing with the postgres databases social-db and cluster-db '''
from sqlalchemy import create_engine, MetaData, Table
from retrying import retry
from config import (CLUSTER_DB_HOST, CLUSTER_DB_NAME, CLUSTER_DB_USER, CLUSTER_DB_PASS,
                    SOCIAL_DB_HOST, SOCIAL_DB_NAME, SOCIAL_DB_USER, SOCIAL_DB_PASS)

db_config = {
    'cluster': {
        'host': CLUSTER_DB_HOST,
        'db_name': CLUSTER_DB_NAME,
        'user': CLUSTER_DB_USER,
        'password': CLUSTER_DB_PASS
    },
    'social': {
        'host': SOCIAL_DB_HOST,
        'db_name': SOCIAL_DB_NAME,
        'user': SOCIAL_DB_USER,
        'password': SOCIAL_DB_PASS
    }
}


ENGINES = {}
CONNECTIONS = {}
METADATA = {}
TABLES = {}


def get_engine(config):
    ''' Get postgres engine for given host and db_name, instantiating a new instance if necessary '''
    key = (config['host'], config['db_name'])
    if key not in ENGINES:
        ENGINES[key] = create_postgres_engine(
            user=config['user'], password=config['password'], db_name=config['db_name'], host=config['host'])
    return ENGINES[key]


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def get_connection(config):
    ''' Get postgres connection for given host and db_name, instantiating a new instance if necessary '''
    key = (config['host'], config['db_name'])
    if key not in CONNECTIONS:
        engine = get_engine(config)
        CONNECTIONS[key] = engine.connect()
    return CONNECTIONS[key]


def get_metadata(config, schema):
    ''' Get sqlalchemy Metadata object for given host, db_name, and schema, instantiating a new instance if necessary '''
    key = (config['host'], config['db_name'], schema)
    if key not in METADATA:
        engine = get_engine(config)
        METADATA[key] = MetaData(bind=engine, reflect=True, schema=schema)
    return METADATA[key]


def get_table(config, schema, table):
    ''' Get sqlalchemy Table object for given host, db_name, schema, and table, instantiating a new instance if necessary '''
    key = (config['host'], config['db_name'], schema, table)
    if key not in TABLES:
        engine = get_engine(config)
        metadata = get_metadata(config, schema)
        TABLES[key] = Table(table, metadata, autoload=True, autoload_with=engine)
    return TABLES[key]


def get_all_tables(config):
    ''' Return a list of all tables in a postgres db given host and db_name '''
    engine = get_engine(config)
    res = engine.execute('SELECT * FROM pg_catalog.pg_tables')
    return [f'{r[0]}.{r[1]}' for r in res]


def get_schema_tables(config, schema):
    ''' Return a list of all tables from a postgres schema '''
    metadata = get_metadata(config, schema)
    return metadata.tables


def get_table_columns(config, schema, table):
    ''' Return a list of all columns from a postgres table '''
    tbl = get_table(config, schema, table)
    return tbl.columns


def create_postgres_engine(host='localhost', db_name='postgres', port=5432, user='postgres', password='', echo=False):
    ''' Return a sqlalchemy engine object for a postgres db given the connection string values '''
    conn_str = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
    return create_engine(conn_str, echo=echo)
