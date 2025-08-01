import sqlite3
from sqlite3 import Error


def create_connection(path):
    connection = sqlite3.connect(path)
    print("Connection to SQLite DB successful")

    return connection


def execute_query(connection, query, values=None):  # values can be tuple
    cursor = connection.cursor()
    if values:
        cursor.execute(query)
    else:
        cursor.execute(query, values)
    connection.commit()
    print(f"Query {query} executed successfully")

    return cursor.get_last_row_id
