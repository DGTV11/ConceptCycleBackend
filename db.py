import sqlite3
from sqlite3 import Error

from debug import printd


def create_connection(path):
    connection = sqlite3.connect(path)
    printd("Connection to SQLite DB successful")

    return connection


def execute_write_query(connection, query, values=None):  # values can be tuple
    cursor = connection.cursor()
    if values:
        cursor.execute(query, values)
    else:
        cursor.execute(query)
    connection.commit()
    printd(f"Query {query} executed successfully")

    return cursor.lastrowid


def execute_read_query(connection, query, values=None):  # values can be tuple
    cursor = connection.cursor()
    if values:
        cursor.execute(query, values)
    else:
        cursor.execute(query)
    printd(f"Query {query} executed successfully")

    return cursor.fetchall()
