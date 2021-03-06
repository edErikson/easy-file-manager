import sqlite3
from contextlib import closing
import os
import logging

logging.basicConfig(filename='db_log.txt', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


sql_command_dict = {
    'first_sql': "CREATE TABLE IF NOT EXISTS file_paths(id integer primary key, file_path text not null unique)",
    'add_data_sql': "INSERT OR IGNORE INTO file_paths(file_path) VALUES (?)",
    'table_name_sql': "SELECT name FROM sqlite_master where type='table'",
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


class MainDatabase:
    @staticmethod
    def first_time_db():
        try:
            db_connection(sql_command_dict['first_sql'])
        except Exception as e:
            logger.exception(f'\nError on string: {e}\n')

    @staticmethod
    def insert_path_data(data):
        db_connection(sql_command_dict['add_data_sql'], (data,))

    @staticmethod
    def db_search(search_str=''):
        search_sql = "SELECT id, file_path FROM file_paths WHERE file_path LIKE'%%%s%%'" % search_str
        return db_connection(search_sql, receive=True)

    @staticmethod
    def db_delete_record(data):
        deletion_sql = "DELETE FROM file_paths WHERE id=?"
        return db_connection(deletion_sql, (data,))


class ExtraDatabase:
    @staticmethod
    def create_table(table_name=''):
        sql_query = "CREATE TABLE IF NOT EXISTS %s(item_id INTEGER PRIMARY KEY, id INTEGER NOT NULL, " \
                    "name TEXT NOT NULL, size INTEGER, FOREIGN KEY (id) REFERENCES file_paths(id))" % table_name
        try:
            db_connection(sql_query)
            logger.info(f'\nCreated table : {table_name}\n')
        except Exception as e:
            logger.exception(f'\nError on string: {e}\n')

    @staticmethod
    def insert_data(item_id, name, size, table_name=''):
        sql_query = "INSERT OR IGNORE INTO %s(id, name, size) VALUES (?, ?, ?)" % table_name
        db_connection(sql_query, (item_id, name, size,))


class DbFunctions:
    @staticmethod
    def sorted_name(table_name=''):
        sql_query = "SELECT id, name, size FROM %s ORDER BY name ASC" % table_name
        return db_connection(sql_query, receive=True)

    @staticmethod
    def sorted_size(table_name=''):
        sql_query = "SELECT id, name, size FROM %s ORDER BY size DESC" % table_name
        return db_connection(sql_query, receive=True)

    @staticmethod
    def get_table_data(table_name=''):
        sql_query = "SELECT id, name, size FROM %s" % table_name
        try:
            return db_connection(sql_query, receive=True)
        except Exception as e:
            logger.exception(f'\nWrong format database : {e} \n')
            sql_query = "SELECT id, file_path FROM %s" % table_name
            return db_connection(sql_query, receive=True)

    @staticmethod
    def get_item_path(data, table_name=''):
        sql = "SELECT file_path FROM file_paths WHERE id IN (SELECT id FROM %s WHERE id=?);" % table_name
        return db_connection(sql, (data,), receive=True)


def get_table_names():
    return db_connection(sql_command_dict['table_name_sql'], receive=True)


def all_table_columns(db_table):
    sql = "PRAGMA table_info(%s)" % db_table
    cursor = db_connection(sql, receive=True)
    names = list(map(lambda x: x[1], cursor))
    return tuple(names)


if __name__ == "__main__":
    if not os.path.isfile("folder.db"):
        print('No database detected, creating...')
        MainDatabase.first_time_db()
    else:
        print('database detected with, \nTable names:  and columns ')
        for table in db_connection(sql_command_dict['table_name_sql'], receive=True):
            print(table[0], all_table_columns(table[0]))
