import pymysql.cursors

from app.utils import logger as _logger
from app.config import get_settings

logger = _logger.get_logger()


class SqlConnection:
    """
    Singleton class
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            settings = get_settings()
            host=settings.SQL_HOST
            user=settings.SQL_USER
            password=settings.SQL_PASSWORD
            database=settings.SQL_DATABASE
            cls._instance.connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                cursorclass=pymysql.cursors.DictCursor
            )
        return cls._instance

    def get_connection(self):
        return self.connection
    

        
