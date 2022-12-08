from connector import MSSQLConnector
from ve_estimator import VEEstimator
from data_processor import DataProcessor
from query_generator import QueryGenerator


def main():
    with MSSQLConnector() as con:
        query_gen = QueryGenerator(age_groups=9, vac_interval_group=True, subjects=['РФ', 'г. Санкт-Петербург',
                                                                                    'Московская область'])
        data_processor = DataProcessor(con.cursor)
        zab_df = data_processor.query_to_df(*query_gen.query_zab_data())
        vac_df = data_processor.query_to_df(*query_gen.query_vac_data())
        zab_vac_df = data_processor.query_to_df(*query_gen.query_zab_vac_data())
        pop_df = data_processor.query_to_df(*query_gen.query_pop_data())
        zab_df.to_csv('../output/zab_df.csv', index=False, encoding='cp1251', na_rep='NULL')
        vac_df.to_csv('../output/vac_df.csv', index=False, encoding='cp1251', na_rep='NULL')
        zab_vac_df.to_csv('../output/zab_vac_df.csv', index=False, encoding='cp1251', na_rep='NULL')
        pop_df.to_csv('../output/pop_df.csv', index=False, encoding='cp1251', na_rep='NULL')

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
