from database.connection import MySQLConnectionManager


class DatabaseObject:
    table = None
    read_query = "SELECT * FROM {table}"
    write_query = None

    @classmethod
    def _get_column_names(cls):
        # TODO: possibly cache this info
        column_names = []
        with MySQLConnectionManager.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f'describe {cls.table}')
                for column_info in cursor:
                    column_names.append(column_info[0])
        return column_names

    @classmethod
    def _get_rows(cls, **kwargs):
        columns = cls._get_column_names()
        for key, value in kwargs.items():
            if key not in columns:
                raise KeyError(f'`{key}` is not a valid column in `{cls.table}`')

        query = cls.read_query.format(table=cls.table)
        parameters = []
        if kwargs:
            query += ' WHERE '
            additions = []
            for key, value in kwargs.items():
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
    def from_db(cls, **kwargs):
        return [cls._db_row_to_obj(row) for row in cls._get_rows(**kwargs)]

    @classmethod
    def _db_row_to_obj(cls, row):
        return cls(**row)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def write_to_db(self):
        raise NotImplementedError()