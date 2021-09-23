import mysql.connector

from misc.exceptions import EmbeddedException
from credentials import DB_ADDRESS, DB_PASSWORD, DB_USERNAME

from .constants import DB_NAME

MAX_OPEN_CONNECTIONS = 10


class MySQLConnection:

    def __init__(self, ):
        self.leased = False
        self._connection = mysql.connector.connect(
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_ADDRESS,
            database=DB_NAME
        )

    def close(self):
        try:
            self._connection.close()
        except Exception as ex:
            # TODO: implement proper logging
            pass

    def __enter__(self):
        self.leased = True
        return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.leased = False
        # TODO
        self.close()


class MySQLConnectionManager:
    _connections: list[MySQLConnection] = []

    @classmethod
    def get_connection(cls):
        return MySQLConnection()
        # TODO
        # connection = next((connection for connection in cls._connections if not connection.leased), None)
        # if not connection:
        #     connection = cls._open_new_connection()
        #     cls._connections.append(connection)
        # return connection

    @classmethod
    def _open_new_connection(cls):
        if len(cls._connections) > MAX_OPEN_CONNECTIONS:
            raise Exception('Failed to create additional db connection, max connections reached!')
        try:
            return MySQLConnection()
        except Exception as ex:
            raise EmbeddedException('Failed to create new db connection', exception=ex)