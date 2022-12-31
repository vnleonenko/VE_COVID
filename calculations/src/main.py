from connector import MSSQLConnector
from ve_estimator import VEEstimator
from data_processor import DataProcessor
from query_generator import QueryGenerator
from argparse import ArgumentParser, FileType
import argparse


class LoadFromFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        data = []
        with values as f:
            for line in f.readlines():
                # parse arguments in the file and store them in the target namespace
                data.append(line.strip())
        setattr(namespace, option_string.lstrip('--'), data)


def get_cli_args():
    parser = ArgumentParser(description="Calculate vaccination efficacy using Generalized Linear Model",
                            allow_abbrev=False)
    parser.add_argument("--age_groups", required=True)
    parser.add_argument("--vac_intervals", action='store_true')
    parser.add_argument("--data_points", default='all', required=False,
                        type=FileType('r', encoding='utf-8'), action=LoadFromFile)
    parser.add_argument("--subjects",  default='all', required=False,
                        type=FileType('r', encoding='utf-8'), action=LoadFromFile)  # action=LoadFromFile)
    return parser


def main():
    parser = get_cli_args()
    cli_args = vars(parser.parse_args(['--age_groups', '3', '--data_points', './data_points.txt',
                                  '--subjects', 'subjects.txt']))  # vars(parser.parse_args())
    data_points = cli_args.get('data_points')
    subjects = cli_args.get('subjects')
    age_groups = int(cli_args.get('age_groups'))
    vac_interval_group = cli_args.get('vac_intervals')

    with MSSQLConnector() as con:
        query_gen = QueryGenerator(age_groups=age_groups, vac_interval_group=vac_interval_group,
                                   subjects=subjects, data_points=data_points)

        data_processor = DataProcessor(con.cursor)
        zab_query, zab_columns = query_gen.query_zab_data()
        vac_query, vac_columns = query_gen.query_vac_data()
        zab_vac_query, zab_vac_columns = query_gen.query_zab_vac_data()

        zab_df = data_processor.query_to_df(zab_query, zab_columns)
        vac_df = data_processor.query_to_df(vac_query, vac_columns)
        zab_vac_df = data_processor.query_to_df(zab_vac_query, zab_vac_columns)
        pop_df = data_processor.query_to_df(*query_gen.query_pop_data())

        if query_gen.vac_interval_group:
            vac_ints = 6
        else:
            vac_ints = 1
        '''zab_df.to_csv(f'../output/infected/zab_df_{query_gen.age_groups}_{vac_ints}.csv',
                      index=False, encoding='cp1251', na_rep='NULL')
        vac_df.to_csv(f'../output/vaccinated/vac_df_{query_gen.age_groups}_{vac_ints}.csv',
                      index=False, encoding='cp1251', na_rep='NULL')
        zab_vac_df.to_csv(f'../output/infected_vaccinated/zab_vac_df_{query_gen.age_groups}_{vac_ints}.csv',
                          index=False, encoding='cp1251', na_rep='NULL')
        pop_df.to_csv(f'../output/population/pop_df_{query_gen.age_groups}_{vac_ints}.csv',
                      index=False, encoding='cp1251', na_rep='NULL')'''

    estimator = VEEstimator(zab_df, vac_df, zab_vac_df, pop_df)
    ve_df = estimator.compute_ve()
    if query_gen.vac_interval_group:
        vac_intervals = '6'
    else:
        vac_intervals = '1'
    ve_df.to_csv(f'../output/ve_{query_gen.age_groups}_{vac_intervals}_.csv',
                 sep=';', index=False, encoding='cp1251', na_rep='NULL')


if __name__ == '__main__':
    main()
