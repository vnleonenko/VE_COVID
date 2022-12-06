import pyodbc
import pandas as pd


class MSSQLConnector:
    def __init__(self):
        self.server = 'tcp:db.influenza.spb.ru,1984'
        self.database = 'VE'
        self.username = 've_access'
        self.password = 'VE@niiGrippa4$'
        self.connection = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};'
                                         'SERVER=' + self.server + ';DATABASE=' + self.database +
                                         ';UID=' + self.username + ';PWD=' + self.password,
                                         autocommit=True)
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.connection.close()
