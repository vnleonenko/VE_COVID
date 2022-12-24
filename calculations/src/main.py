from connector import MSSQLConnector
from ve_estimator import VEEstimator
from data_processor import DataProcessor
from query_generator import QueryGenerator


def main():
    with MSSQLConnector() as con:

        query_gen = QueryGenerator(age_groups=9, vac_interval_group=True, subjects=['Московская область', 'РФ',
                                   'г. Санкт-Петербург'], data_points=['2022.08.B_16-09-2022',
                                                                       '2022.09.B_11-11-2022',
                                                                       '2022.10.B_13-12-2022',
                                                                       '2022.11.B_21-12-2022'])
        data_processor = DataProcessor(con.cursor)
        zab_query, zab_columns = query_gen.query_zab_data()
        vac_query, vac_columns = query_gen.query_vac_data()
        zab_vac_query, zab_vac_columns = query_gen.query_zab_vac_data()

        '''with open('../output/vac_view_query_test.sql', 'w', encoding='cp1251') as f:
            f.write(vac_query)
        with open('../output/zab_vac_view_query.sql', 'w', encoding='cp1251') as f:
            f.write(zab_vac_query)'''

        zab_df = data_processor.query_to_df(zab_query, zab_columns)
        vac_df = data_processor.query_to_df(vac_query, vac_columns)
        zab_vac_df = data_processor.query_to_df(zab_vac_query, zab_vac_columns)
        pop_df = data_processor.query_to_df(*query_gen.query_pop_data())

        if query_gen.vac_interval_group:
            vac_ints = 6
        else:
            vac_ints = 1
        zab_df.to_csv(f'../output/infected/zab_df_{query_gen.age_groups}_{vac_ints}.csv',
                      index=False, encoding='cp1251', na_rep='NULL')
        vac_df.to_csv(f'../output/vaccinated/vac_df_{query_gen.age_groups}_{vac_ints}.csv',
                      index=False, encoding='cp1251', na_rep='NULL')
        zab_vac_df.to_csv(f'../output/infected_vaccinated/zab_vac_df_{query_gen.age_groups}_{vac_ints}.csv',
                          index=False, encoding='cp1251', na_rep='NULL')
        pop_df.to_csv(f'../output/population/pop_df_{query_gen.age_groups}_{vac_ints}.csv',
                      index=False, encoding='cp1251', na_rep='NULL')

    estimator = VEEstimator(zab_df, vac_df, zab_vac_df, pop_df)
    ve_df = estimator.compute_ve()
    if query_gen.vac_interval_group:
        vac_intervals = '6'
    else:
        vac_intervals = '0'
    ve_df.to_csv(f'../output/ve_{query_gen.age_groups}_age_groups_{vac_intervals}_vac_intervals.csv',
                 sep=';', index=False, encoding='cp1251', na_rep='NULL')


if __name__ == '__main__':
    main()
