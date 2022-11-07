import pandas as pd
from utils import connect_to_db, query_to_df


def get_general_ve(data_points, crs):
    columns = ['region']
    cases = ['zab', 'st', 'tyazh', 'sm']
    ages = ['18_59', '18_59_R', '60', '60_R', 'total', 'total_R']
    for case in cases:
        for age in ages:
            columns.append(f'{case}_ve_{age}')
            if age[-1] == 'R':
                columns.append(f'{case}_cil_{age}')
                columns.append(f'{case}_cih_{age}')
    ve = []
    vac_indices = ['', '1', '3', '4', '5']
    vaccine = ''
    for data_point in data_points:
        for vac_ind in vac_indices:
            ve_query = f'''
            set arithabort off
            set ansi_warnings off
            
            select * from dbo.VE_W_CI('{data_point}', '{vac_ind}')
            '''
            df = query_to_df(ve_query, crs, columns)
            df.insert(0, 'data_point', data_point)

            if vac_ind == '':
                vaccine = 'AllVaccines'
            elif vac_ind == '1':
                vaccine = 'SputnikV'
            elif vac_ind == '3':
                vaccine = 'EpiVacCorona'
            elif vac_ind == '4':
                vaccine = 'CoviVac'
            elif vac_ind == '5':
                vaccine = 'SputnikLite'
            df.insert(1, 'vaccine', vaccine)
            ve.append(df)

    return pd.concat(ve, ignore_index=True)


if __name__ == '__main__':
    cursor = connect_to_db()
    data_points_query = '''select distinct(data_point) from dbo.ZAB_VAC where data_point not like '%[B]%' '''
    data_points = [data_point[0] for data_point in cursor.execute(data_points_query).fetchall()]
    ve = get_general_ve(data_points, cursor)
    ve.to_csv('../../app/data/input_csv_files/general/general_ve.csv', sep=';',
              index=False, encoding='cp1251', na_rep='NULL')
