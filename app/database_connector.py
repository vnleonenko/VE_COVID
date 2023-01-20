import pandas as pd
import pyodbc
import os


class MSSQL:
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

    def query_to_df(self, query, columns, *args):
        query_res = list(map(list, self.cursor.execute(query, args).fetchall()))
        return pd.DataFrame(query_res, columns=columns)

    @staticmethod
    def _get_columns():
        columns = ['data_point', 'region', 'age_group',
                   'vac_interval_group', 'vaccine']
        cases = ['zab', 'hosp', 'severe', 'death']
        prefix = ['ve_', 'cil_', 'cih_']
        for case in cases:
            for pref in prefix:
                columns.append(pref + case)
        return columns

    def extract_ve(self, age, vaccine=None, subject=None, age_groups=3, vac_intervals=6):
        data_point_clause = ''
        if age_groups > 3 and vac_intervals == 1:
            data_point_clause = "like '%[B]%' and vac_interval_group = '21_195_days'"
        elif age_groups == 3 and vac_intervals == 1:
            data_point_clause = "not like '%[B]%' and vac_interval_group = '21_195_days'"
        elif age_groups == 3 and vac_intervals == 6:
            data_point_clause = "not like '%[B]%' and vac_interval_group not like '21_195_days'"
        elif age_groups > 3 and vac_intervals == 6:
            data_point_clause = "like '%[B]%' and vac_interval_group not like '21_195_days'"

        query = f'''select * from dbo.VE_TEST where data_point {data_point_clause}
                and age_group = '{age}'  '''
        if subject is not None:
            query = query + f'''and region = '{subject}' '''
        if vaccine is not None:
            query = query + f'''and vaccine = '{vaccine}' '''

        df = self.query_to_df(query, self._get_columns())

        return df

    def __exit__(self, *args, **kwargs):
        self.connection.close()
