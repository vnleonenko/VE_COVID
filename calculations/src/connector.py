import pyodbc
import numpy as np
import pandas as pd
from tqdm import tqdm


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

    def unload_ve(self, csv_path):

        ve_df = pd.read_csv(csv_path, encoding='cp1251', delimiter=';')
        ve_df.iloc[:, 5:] = ve_df.iloc[:, 5:].astype('float64')
        ve_df = ve_df.replace([np.nan, -np.inf, np.inf], None)
        table_name = 'dbo.VE_VE_EST'
        values = ','.join(['?' for _ in range(len(ve_df.columns))])
        insert_query = f'''insert into {table_name} values ({values})'''

        print('Data unloading to VE_VE_EST table is starting')
        for i in tqdm(range(ve_df.shape[0])):
            try:
                self.cursor.execute(insert_query, ve_df.iloc[i, :].tolist())
            except pyodbc.IntegrityError as e:
                print(e)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.connection.close()
