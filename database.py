#!/usr/bin/python3
from configparser import ConfigParser
import asyncpg
import asyncio

def config(filename='config/database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    print('Config parsed from {0}'.format(filename))
    return db

async def connect():
    """ Connect to the PostgreSQL database server """
    print("connection")
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = await asyncpg.connect(**params)

        # execute a statement
        print('PostgreSQL database version:')
        await conn.execute('SELECT version()')
        return conn
    except Exception as error:
        print(error)

async def disconnect(connection):
    if not connection.is_closed():
        try:
            await connection.close()
            print('Database connection closed')
        except Exception as error:
            print(error)

async def create_table(connection):
    if connection.is_closed():
        raise Exception("The connection is closed")
    else:
        print('Creating the table...')
        await connection.execute(
                '''
                CREATE TABLE categories 
                (
                    cat BIGINT PRIMARY KEY, -- ||
                    roles   BIGINT ARRAY
                );
                ''')
        print('Table categories created')

async def is_table(connection):
    if connection.is_closed():
        raise Exception("The connection is closed")
    else:
        print('Checking if the table exist...')
        r = await connection.fetchrow('''
        SELECT EXISTS
        (
            SELECT 1
            FROM pg_tables
            WHERE tablename = 'categories'
        );
        ''')
        return r[0]
