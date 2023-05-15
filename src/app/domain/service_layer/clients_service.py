from typing import Any

from fastapi import Depends
from pymysql import IntegrityError

from app.config import Settings, get_settings
from app.adapters.sql_connection import SqlConnection



class ClientsService:

    def __init__(
            self,
            settings: Settings = Depends(get_settings),
            connection: SqlConnection = Depends()
    ) -> None:
        self.settings = settings
        self.connection = connection.get_connection()

    class ObjectAlreadyExists(Exception):
        pass

    class ObjectDoesNotExist(Exception):
        def __init__(self) -> None:
            super().__init__("object does not exist")

    def create_client(
            self,
            phone: str,
            name: str,
            last_name: str,
            age: str
    ) -> bool:
        try:
            sql = "INSERT INTO clients (phone, name, last_name, age) VALUES (%s, %s, %s, %s)"
            values = (phone, name, last_name, str(age))
            cursor = self.connection.cursor()
            cursor.execute(sql, values)
            self.connection.commit()
            return True
        except IntegrityError as e:
            raise self.ObjectAlreadyExists(str(e))

    def list_clients(self) -> list:
        sql = "Select * from clients"
        cursor = self.connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
        

    def get_client(self, client_phone: str) -> any:
        sql = "Select * from clients WHERE phone = %s;"
        cursor = self.connection.cursor()
        cursor.execute(sql, client_phone)
        client = cursor.fetchone()
        if not client:
            raise self.ObjectDoesNotExist()
        
        return client

        
    
