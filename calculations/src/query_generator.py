import pandas as pd


class QueryGenerator:
    def __init__(self, age_groups, vac_interval_group=True, gender=False, subjects='all'):
        self.age_groups = age_groups
        self.vac_interval_group = vac_interval_group
        self.gender = gender
        if age_groups == 3:
            self.age_group_filter = "('18-59', '60+')"
            self.data_point_filter = "not like '%[B]%'"
        elif age_groups > 3:
            self.data_point_filter = "like '%[B]%'"
            self.age_group_filter = "('20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+')"
        self.subjects = subjects

    def query_pop_data(self):
        columns = ['region', 'age_group', 'population']
        res_query = ''
        if self.age_groups == 3:
            res_query = f'''select region, 
                        case when age_group = 'nas_age_18_59_total' then '18-59'
                             when age_group = 'nas_age_60_total' then '60+' 
                             when age_group = 'nas_age_adult_total' then '18+' 
                             end as age_group, population
                        from dbo.NAS_AGE unpivot(population for age_group in ([nas_age_18_59_total], 
                                                                              [nas_age_60_total], 
                                                                              [nas_age_adult_total]))
                        as unpivot_table'''

        elif self.age_groups > 3:
            res_query = f'''select region, 
                        case when age_group = 'nas_age_20_29_total' then '20-29'
                             when age_group = 'nas_age_30_39_total' then '30-39' 
                             when age_group = 'nas_age_40_49_total' then '40-49'
                             when age_group = 'nas_age_50_59_total' then '50-59'
                             when age_group = 'nas_age_60_69_total' then '60-69'
                             when age_group = 'nas_age_70_79_total' then '70-79'
                             when age_group = 'nas_age_80_total' then '80+'
                             when age_group = 'nas_age_adult_total' then '18+' 
                             end as age_group, population
                        from dbo.NAS_AGE10 
                        unpivot(population for age_group in
                        ([nas_age_20_29_total], [nas_age_30_39_total], [nas_age_40_49_total],
                        [nas_age_50_59_total],  [nas_age_60_69_total], [nas_age_70_79_total],
                        [nas_age_80_total], [nas_age_adult_total])) as unpivot_table'''

        res_query = f'''select sq1.* from ({res_query}) as sq1
                    where region in ('{"', '".join(self.subjects)}')'''

        return res_query, columns

    def query_zab_data(self):
        columns = ['data_point', 'region', 'age_group', 'count_zab', 'count_hosp', 'count_severe', 'count_death']
        select_columns = ', '.join([c if 'count' not in c else f'sum({c}) as {c}' for c in columns])
        init_query = f'''select {select_columns} from dbo.ZAB_VIEW
                     where data_point {self.data_point_filter} and age_group in {self.age_group_filter}
                     group by data_point, region, age_group
                     '''
        res_query = self._group_by_age(columns, columns[:3], init_query)
        res_query = self._group_by_subjects(columns, columns[:3], res_query)
        res_query = f'''select sq1.* from ({res_query}) as sq1 where region in ('{"', '".join(self.subjects)}')'''
        return res_query, columns

    def query_zab_vac_data(self):
        columns = ['data_point', 'region', 'age_group', 'vac_interval_group', 'vaccine',
                   'count_vac_zab', 'count_vac_hosp', 'count_vac_severe', 'count_vac_death']

        select_columns = ', '.join([c if 'count' not in c else f'sum({c}) as {c}' for c in columns])

        init_query = f'''select {select_columns} from dbo.ZAB_VAC_VIEW
                    where data_point {self.data_point_filter} and age_group in {self.age_group_filter}
                    group by data_point, region, age_group, vac_interval_group, vaccine'''
        res_query = self._group_by_age(columns, columns[:5], init_query)
        res_query = self._group_by_subjects(columns, columns[:5], res_query)
        res_query = self._group_by_vaccines(columns, columns[:5], res_query)

        res_query = f'''select sq1.* from ({res_query}) as sq1 where region in ('{"', '".join(self.subjects)}')'''

        return res_query, columns

    def query_vac_data(self):
        columns = ['data_point', 'region', 'vac_interval_group', 'age_group', 'vaccine', 'vac_count']
        select_columns = ', '.join([c if c != 'vac_count' else f'sum({c}) as {c}' for c in columns])
        init_query = f'''select {select_columns} from dbo.VAC_VIEW
                        where data_point {self.data_point_filter} and age_group in {self.age_group_filter}
                        group by data_point, region, vac_interval_group, age_group, vaccine'''
        res_query = self._group_by_age(columns, columns[:5], init_query)
        res_query = self._group_by_subjects(columns, columns[:5], res_query)
        res_query = self._group_by_vaccines(columns, columns[:5], res_query)
        res_query = f'''select sq1.* from ({res_query}) as sq1 where region in ('{"', '".join(self.subjects)}')'''
        return res_query, columns

    def _group_by_age(self, columns, groupby_columns, init_query):
        select_sq1_columns = ', '.join([f'sq1.{c}' if c != 'age_group'
                                        else f"case when sq1.{c} in {self.age_group_filter} then '18+' end as {c}"
                                        for c in columns])
        subquery1 = f'''select {select_sq1_columns} from ({init_query}) as sq1'''

        select_sq2_columns = ', '.join([f'sq2.{c}' if 'count' not in c else f'sum(sq2.{c}) as {c}'
                                        for c in columns])
        groupby_sq2_columns = ', '.join([f'sq2.{c}' for c in groupby_columns])
        subquery2 = f'''select {select_sq2_columns} from ({subquery1}) as sq2 group by {groupby_sq2_columns}'''
        return f'''{init_query} union {subquery2}'''

    def _group_by_subjects(self, columns, groupby_columns, init_query):
        select_sq1_columns = ', '.join([f'sq1.{c}' if c != 'region'
                                        else f"case when sq1.{c} not like 'РФ' then 'РФ' end as {c}"
                                        for c in columns])
        subquery1 = f'''select {select_sq1_columns} from ({init_query}) as sq1'''

        select_sq2_columns = ', '.join([f'sq2.{c}' if 'count' not in c else f'sum(sq2.{c}) as {c}'
                                        for c in columns])
        groupby_sq2_columns = ', '.join([f'sq2.{c}' for c in groupby_columns])
        subquery2 = f'''select {select_sq2_columns} from ({subquery1}) as sq2 group by {groupby_sq2_columns}
                    '''

        return f'''{init_query} union {subquery2}'''

    def _group_by_vaccines(self, columns, groupby_columns, init_query):
        select_sq1_columns = ', '.join([f'sq1.{c}' if c != 'vaccine'
                                        else f"case when sq1.{c} not like 'AllVaccines' then 'AllVaccines' end as {c}"
                                        for c in columns])
        subquery1 = f'''select {select_sq1_columns} from ({init_query}) as sq1'''

        select_sq2_columns = ', '.join([f'sq2.{c}' if 'count' not in c else f'sum(sq2.{c}) as {c}'
                                        for c in columns])
        groupby_sq2_columns = ', '.join([f'sq2.{c}' for c in groupby_columns])
        subquery2 = f'''select {select_sq2_columns} from ({subquery1}) as sq2 group by {groupby_sq2_columns}
                            '''

        return f'''{init_query} union {subquery2}'''



