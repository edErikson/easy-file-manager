import sqlite3
from contextlib import closing
import os


sql_command_dict = {
    'first_sql': "CREATE TABLE IF NOT EXISTS file_paths(id integer primary key, file_path text not null unique)",
    'add_data_sql': "INSERT OR IGNORE INTO file_paths(file_path) VALUES (?)",

    'table_name_sql': "SELECT name FROM sqlite_master where type='table'",
    'column_name_sql': "PRAGMA table_info(file_paths)",

    'all_data': "SELECT file_path FROM file_paths",
    }


def db_connection(sql_task, data=None, receive=False):
    with sqlite3.connect('folder.db') as db:
        with closing(db.cursor()) as c:
            if data:
                c.execute(sql_task, data)
            else:
                c.execute(sql_task)
            if receive:
                return c.fetchall()
            for item in c:
                return item


def first_time_db():
    try:
        db_connection(sql_command_dict['first_sql'])
    except Exception as e:
        print('Error on string: ', e)


def insert_data(data):
    db_connection(sql_command_dict['add_data_sql'], (data,))


def db_search(search_str=''):
    search_sql = f"SELECT file_path FROM file_paths WHERE file_path LIKE'%{search_str}%'"
    return db_connection(search_sql, receive=True)


def get_column_names():
    cursor = db_connection(sql_command_dict['column_name_sql'], receive=True)
    names = list(map(lambda x: x[1], cursor))
    return tuple(names)


if __name__ == "__main__":
    if not os.path.isfile("folder.db"):
        print('No database detected, creating...')
        first_time_db()
    else:
        print('database detected with, \nTable name: ')
        print(db_connection(sql_command_dict['table_name_sql']))
        print('columns : ', get_column_names())
