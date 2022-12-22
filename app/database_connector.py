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


"""query = f'''
        select sq1.data_point, sq1.region, sq1.age_group, sq1.vaccine,
        sum(sq1.ve_zab) as ve_zab, sum(sq1.cil_zab) as cil_zab, sum(sq1.cih_zab) as cih_zab,
        sum(sq1.ve_hosp) as ve_hosp, sum(sq1.cil_hosp) as cil_hosp, sum(sq1.cih_hosp) as cih_hosp,
        sum(sq1.ve_severe) as ve_severe, sum(sq1.cil_severe) as cil_severe, sum(sq1.cih_severe) as cih_severe,
        sum(sq1.ve_death) as ve_death, sum(sq1.cil_death) as cil_death, sum(sq1.cih_death) as cih_death
        from
        (select data_point, 
        case when reg_id = {subject_id} then '{subject_value}' end as region,
        case when age_id = {age_id} then '{age_value}' end as age_group,
        case when vaccine_id = {vaccine_id} then '{vaccine_value}' end as vaccine,

        case when case_type = 1 then ve end as ve_zab,
        case when case_type = 1 then cil end as cil_zab,
        case when case_type = 1 then cih end as cih_zab,

        case when case_type = 2 then ve end as ve_hosp,
        case when case_type = 2 then cil end as cil_hosp,
        case when case_type = 2 then cih end as cih_hosp,

        case when case_type = 3 then ve end as ve_severe,
        case when case_type = 3 then cil end as cil_severe,
        case when case_type = 3 then cih end as cih_severe,

        case when case_type = 4 then ve end as ve_death,
        case when case_type = 4 then cil end as cil_death,
        case when case_type = 4 then cih end as cih_death             
        from dbo.VE_CI 
        where reg_id = {subject_id} and vaccine_id = {vaccine_id} and age_id = {age_id}
        ) as sq1
        group by sq1.data_point, sq1.region, sq1.vaccine, sq1.age_group'''"""


