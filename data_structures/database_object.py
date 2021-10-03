from uuid import uuid4
from datetime import datetime
from typing import Iterable
from database.connection import MySQLConnectionManager
from database.constants import DB_NAME

from misc.exceptions import EmbeddedException


class DatabaseObject:
    _table = None
    _column_names = None
    _read_query = 'SELECT * FROM {db_name}.{table} '
    _write_query = 'REPLACE INTO {db_name}.{table} VALUES {values}'

    @classmethod
    def _get_column_names(cls):
        # TODO: possibly cache this info, this does mean restarting the web-app when data-base is updated
        if not cls._column_names:
            column_names = []
            with MySQLConnectionManager.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f'describe {DB_NAME}.{cls._table}')
                    for column_info in cursor:
                        column_names.append(column_info[0])
            cls._column_names =column_names
        return cls._column_names

    @classmethod
    def _get_rows(cls, **kwargs):
        columns = cls._get_column_names()
        for key, value in kwargs.items():
            if key not in columns:
                raise KeyError(f'`{key}` is not a valid column in `{cls._table}`')

        query = cls._read_query.format(db_name=DB_NAME, table=cls._table)
        parameters = []
        if kwargs:
            query += 'WHERE '
            additions = []
            for key, value in kwargs.items():
                if isinstance(value, Iterable):
                    additions.append(f'{key} in ({", ".join("%s" for _ in range(0, len(value)))}) ')
                    parameters += list(value)
                else:
                    additions.append(f'{key} = %s ')
                    parameters.append(value)
            query += 'AND '.join(additions)

        rows = []
        with MySQLConnectionManager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(parameters))
                for row in cursor:
                    rows.append({columns[idx]: column_value for idx, column_value in enumerate(row)})
        return rows

    @classmethod
    def bulk_write_to_db(cls, instances):
        if not instances:
            return

        value_sets = []
        for instance in instances:
            values = instance._obj_to_db_values()
            if not values:
                raise Exception('Need values to insert into table')
            value_sets.append(values)

        value_str = ', '.join(
            '(' + ', '.join('%s' for _ in range(len(value_set))) + ')'
            for value_set in value_sets
        )
        # TODO: DEBUG LOGGING
        print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Writing to DB')
        query = cls._write_query.format(
            db_name=DB_NAME,
            table=cls._table,
            values=value_str
        )
        try:
            with MySQLConnectionManager.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, tuple([value for value_set in value_sets for value in value_set]))
                connection.commit()
        except Exception as ex:
            raise EmbeddedException('Failed to insert new rows', exception=ex)


    @classmethod
    def from_db(cls, **kwargs):
        return iter([cls._db_row_to_obj(row) for row in cls._get_rows(**kwargs)])

    @classmethod
    def _db_row_to_obj(cls, row):
        return cls(**row)

    def __init__(self, id=None, **kwargs):
        self.id = id if id is not None else str(uuid4())

    def write_to_db(self):
        return self.bulk_write_to_db([self])

    def _obj_to_db_values(self):
        values = []
        for column in self._get_column_names():
            values.append(getattr(self, column))
        return values
