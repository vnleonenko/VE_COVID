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

    @staticmethod
    def _get_ve_columns():
        columns = ['data_point', 'region', 'vac_interval_group', 'vaccine']
        ages = ['_18_59', '_60', '_total']
        cases = ['_zab', '_hosp', '_severe', '_death']
        prefix = ['ve', 'cil', 'cih']
        for age in ages:
            for case in cases:
                for pref in prefix:
                    columns.append(pref + case + age)
        return columns

    def _query_to_df(self, query, columns, *args):
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

    def extract_int_ve(self, ages_split=True):
        if ages_split:
            data_point_clause = "like '%[B]%'"
        else:
            data_point_clause = "not like '%[B]%'"
        query = f'''select * from dbo.VE_TEST where data_point {data_point_clause} '''
        df = self._query_to_df(query, self._get_columns())

        return df

    def extract_general_ve(self):
        query = f'''select sq1.data_point, sq1.region, sq1.vaccine_id as vaccine,
                    sum(ve_zab_18_59) as ve_zab_18_59,
                    sum(cil_zab_18_59) as cil_zab_18_59,
                    sum(cih_zab_18_59) as cih_zab_18_59,
                    sum(ve_zab_60) as ve_zab_60,
                    sum(cil_zab_60) as cil_zab_60,
                    sum(cih_zab_60) as cih_zab_60,
                    sum(ve_zab_total) as ve_zab_total,
                    sum(cil_zab_total) as cil_zab_total,
                    sum(cih_zab_total) as cih_zab_total,

                    sum(ve_hosp_18_59) as ve_hosp_18_59,
                    sum(cil_hosp_18_59) as cil_hosp_18_59,
                    sum(cih_hosp_18_59) as cih_hosp_18_59,
                    sum(ve_hosp_60) as ve_hosp_60,
                    sum(cil_hosp_60) as cil_hosp_60,
                    sum(cih_hosp_60) as cih_hosp_60,
                    sum(ve_hosp_total) as ve_hosp_total,
                    sum(cil_hosp_total) as cil_hosp_total,
                    sum(cih_hosp_total) as cih_hosp_total,

                    sum(ve_severe_18_59) as ve_severe_18_59,
                    sum(cil_severe_18_59) as cil_severe_18_59,
                    sum(cih_severe_18_59) as cih_severe_18_59,
                    sum(ve_severe_60) as ve_severe_60,
                    sum(cil_severe_60) as cil_severe_60,
                    sum(cih_severe_60) as cih_severe_60,
                    sum(ve_severe_total) as ve_severe_total,
                    sum(cil_severe_total) as cil_severe_total,
                    sum(cih_severe_total) as cih_severe_total,

                    sum(ve_death_18_59) as ve_death_18_59,
                    sum(cil_death_18_59) as cil_death_18_59,
                    sum(cih_death_18_59) as cih_death_18_59,
                    sum(ve_death_60) as ve_death_60,
                    sum(cil_death_60) as cil_death_60,
                    sum(cih_death_60) as cih_death_60,
                    sum(ve_death_total) as ve_death_total,
                    sum(cil_death_total) as cil_death_total,
                    sum(cih_death_total) as cih_death_total

                    from 
                        (select  dbo.VE_CI.data_point, dbo.VE_CI.vaccine_id, dbo.REG_IDS.*,
                        case when (dbo.VE_CI.age_id = 18 and dbo.VE_CI.case_type = 1) then dbo.VE_CI.ve else 0 end as ve_zab_18_59,
                        case when (dbo.VE_CI.age_id = 60 and dbo.VE_CI.case_type = 1) then dbo.VE_CI.ve else 0 end as ve_zab_60,
                        case when (dbo.VE_CI.age_id = 99 and dbo.VE_CI.case_type = 1) then dbo.VE_CI.ve else 0 end as ve_zab_total,
                        case when (dbo.VE_CI.age_id = 18 and dbo.VE_CI.case_type = 1) then dbo.VE_CI.cil else 0 end as cil_zab_18_59,
                        case when (dbo.VE_CI.age_id = 60 and dbo.VE_CI.case_type = 1) then dbo.VE_CI.cil else 0 end as cil_zab_60,
                        case when (dbo.VE_CI.age_id = 99 and dbo.VE_CI.case_type = 1) then dbo.VE_CI.cil else 0 end as cil_zab_total,
                        case when (dbo.VE_CI.age_id = 18 and dbo.VE_CI.case_type = 1) then dbo.VE_CI.cih else 0 end as cih_zab_18_59,
                        case when (dbo.VE_CI.age_id = 60 and dbo.VE_CI.case_type = 1) then dbo.VE_CI.cih else 0 end as cih_zab_60,
                        case when (dbo.VE_CI.age_id = 99 and dbo.VE_CI.case_type = 1) then dbo.VE_CI.cih else 0 end as cih_zab_total,

                        case when (dbo.VE_CI.age_id = 18 and dbo.VE_CI.case_type = 2) then dbo.VE_CI.ve else 0 end as ve_hosp_18_59,
                        case when (dbo.VE_CI.age_id = 60 and dbo.VE_CI.case_type = 2) then dbo.VE_CI.ve else 0 end as ve_hosp_60,
                        case when (dbo.VE_CI.age_id = 99 and dbo.VE_CI.case_type = 2) then dbo.VE_CI.ve else 0 end as ve_hosp_total,
                        case when (dbo.VE_CI.age_id = 18 and dbo.VE_CI.case_type = 2) then dbo.VE_CI.cil else 0 end as cil_hosp_18_59,
                        case when (dbo.VE_CI.age_id = 60 and dbo.VE_CI.case_type = 2) then dbo.VE_CI.cil else 0 end as cil_hosp_60,
                        case when (dbo.VE_CI.age_id = 99 and dbo.VE_CI.case_type = 2) then dbo.VE_CI.cil else 0 end as cil_hosp_total,
                        case when (dbo.VE_CI.age_id = 18 and dbo.VE_CI.case_type = 2) then dbo.VE_CI.cih else 0 end as cih_hosp_18_59,
                        case when (dbo.VE_CI.age_id = 60 and dbo.VE_CI.case_type = 2) then dbo.VE_CI.cih else 0 end as cih_hosp_60,
                        case when (dbo.VE_CI.age_id = 99 and dbo.VE_CI.case_type = 2) then dbo.VE_CI.cih else 0 end as cih_hosp_total,

                        case when (dbo.VE_CI.age_id = 18 and dbo.VE_CI.case_type = 3) then dbo.VE_CI.ve else 0 end as ve_severe_18_59,
                        case when (dbo.VE_CI.age_id = 60 and dbo.VE_CI.case_type = 3) then dbo.VE_CI.ve else 0 end as ve_severe_60,
                        case when (dbo.VE_CI.age_id = 99 and dbo.VE_CI.case_type = 3) then dbo.VE_CI.ve else 0 end as ve_severe_total,
                        case when (dbo.VE_CI.age_id = 18 and dbo.VE_CI.case_type = 3) then dbo.VE_CI.cil else 0 end as cil_severe_18_59,
                        case when (dbo.VE_CI.age_id = 60 and dbo.VE_CI.case_type = 3) then dbo.VE_CI.cil else 0 end as cil_severe_60,
                        case when (dbo.VE_CI.age_id = 99 and dbo.VE_CI.case_type = 3) then dbo.VE_CI.cil else 0 end as cil_severe_total,
                        case when (dbo.VE_CI.age_id = 18 and dbo.VE_CI.case_type = 3) then dbo.VE_CI.cih else 0 end as cih_severe_18_59,
                        case when (dbo.VE_CI.age_id = 60 and dbo.VE_CI.case_type = 3) then dbo.VE_CI.cih else 0 end as cih_severe_60,
                        case when (dbo.VE_CI.age_id = 99 and dbo.VE_CI.case_type = 3) then dbo.VE_CI.cih else 0 end as cih_severe_total,

                        case when (dbo.VE_CI.age_id = 18 and dbo.VE_CI.case_type = 4) then dbo.VE_CI.ve else 0 end as ve_death_18_59,
                        case when (dbo.VE_CI.age_id = 60 and dbo.VE_CI.case_type = 4) then dbo.VE_CI.ve else 0 end as ve_death_60,
                        case when (dbo.VE_CI.age_id = 99 and dbo.VE_CI.case_type = 4) then dbo.VE_CI.ve else 0 end as ve_death_total,
                        case when (dbo.VE_CI.age_id = 18 and dbo.VE_CI.case_type = 4) then dbo.VE_CI.cil else 0 end as cil_death_18_59,
                        case when (dbo.VE_CI.age_id = 60 and dbo.VE_CI.case_type = 4) then dbo.VE_CI.cil else 0 end as cil_death_60,
                        case when (dbo.VE_CI.age_id = 99 and dbo.VE_CI.case_type = 4) then dbo.VE_CI.cil else 0 end as cil_death_total,
                        case when (dbo.VE_CI.age_id = 18 and dbo.VE_CI.case_type = 4) then dbo.VE_CI.cih else 0 end as cih_death_18_59,
                        case when (dbo.VE_CI.age_id = 60 and dbo.VE_CI.case_type = 4) then dbo.VE_CI.cih else 0 end as cih_death_60,
                        case when (dbo.VE_CI.age_id = 99 and dbo.VE_CI.case_type = 4) then dbo.VE_CI.cih else 0 end as cih_death_total

                        from dbo.VE_CI
                        join dbo.REG_IDS
                        on dbo.VE_CI.reg_id = dbo.REG_IDS.reg_id
                    ) as sq1
                    group by sq1.data_point, sq1.vaccine_id, sq1.region
                    order by sq1.data_point, sq1.vaccine_id, sq1.region 
                    '''
        columns = self._get_ve_columns()
        columns.remove('vac_interval_group')
        df = self._query_to_df(query, columns)
        vaccines = {1: 'SputnikV', 3: 'EpiVacCorona', 4: 'CoviVac', 5: 'SputnikLite', 99: 'AllVaccines'}
        df['vaccine'] = df['vaccine'].replace(vaccines)
        return df

    def __exit__(self, *args, **kwargs):
        self.connection.close()


