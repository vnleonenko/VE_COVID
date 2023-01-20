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
    subparsers = parser.add_subparsers(dest='command')

    compute_parser = subparsers.add_parser('compute_ve', help='Compute VE via created connection'
                                                              'to database')
    push_parser = subparsers.add_parser('unload_ve', help='Upload calculated VE to the database')

    compute_parser.add_argument('--age_groups', required=True)
    compute_parser.add_argument('--vac_intervals', action='store_true')
    compute_parser.add_argument('--data_points', required=False, type=FileType('r', encoding='utf-8'),
                                action=LoadFromFile)
    compute_parser.add_argument('--subjects',  required=False, type=FileType('r', encoding='utf-8'),
                                action=LoadFromFile)

    push_parser.add_argument('--file_path', required=True, type=str)

    return parser


def main():
    parser = get_cli_args()
    cli_args = parser.parse_args()
    # ['--age_groups', '3', '--data_points', './input/data_points.txt',
    # '--subjects', './input/subjects.txt']
    if cli_args.command == 'compute_ve':
        data_points = cli_args.data_points
        subjects = cli_args.subjects
        age_groups = int(cli_args.age_groups)
        vac_interval_group = cli_args.vac_intervals

        with MSSQLConnector() as con:
            query_gen = QueryGenerator(age_groups=age_groups, vac_interval_group=vac_interval_group,
                                       subjects=subjects, data_points=data_points)
            # add execution info
            data_processor = DataProcessor(con.cursor)
            zab_query, zab_columns = query_gen.query_zab_data()
            vac_query, vac_columns = query_gen.query_vac_data()
            zab_vac_query, zab_vac_columns = query_gen.query_zab_vac_data()

            zab_df = data_processor.query_to_df(zab_query, zab_columns)
            vac_df = data_processor.query_to_df(vac_query, vac_columns)
            zab_vac_df = data_processor.query_to_df(zab_vac_query, zab_vac_columns)
            pop_df = data_processor.query_to_df(*query_gen.query_pop_data())

        estimator = VEEstimator(zab_df, vac_df, zab_vac_df, pop_df)
        ve_df = estimator.compute_ve()
        if query_gen.vac_interval_group:
            vac_intervals = '6'
        else:
            vac_intervals = '1'
        # write output path check if output folder was deleted or absent
        ve_df.to_csv(f'./output/ve/ve_{query_gen.age_groups}_{vac_intervals}.csv',
                     sep=';', index=False, encoding='cp1251', na_rep='NULL')

    elif cli_args.command == 'unload_ve':
        if cli_args.file_path is not None:
            file_path = cli_args.file_path
            with MSSQLConnector() as con:
                con.unload_ve(file_path)
        else:
            print(f'Path to the csv file containing ve estimations has to be provided. '
                  f'Got { cli_args.file_path} instead.')
    else:
        print('Specify command to execute: compute_ve or unload_ve')


if __name__ == '__main__':
    main()
