import pyodbc
import pandas as pd


def connect_to_db():
    server = 'tcp:db.influenza.spb.ru,1984'
    database = 'VE'
    username = 've_access'
    password = 'VE@niiGrippa4$'
    cnxn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};'
                          'SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    return cnxn.cursor()


def query_to_df(query, cursor, columns):
    query_res = list(map(list, cursor.execute(query).fetchall()))
    return pd.DataFrame(query_res, columns=columns)


def group_by_subjects(data_frame):
    agg_dict = {}
    columns_to_groupby = ['data_point', 'vac_interval_group', 'vaccine']
    for agg_column in data_frame.columns:
        if agg_column == 'region':
            agg_dict.update({agg_column: lambda x: 'РФ'})
        elif agg_column in columns_to_groupby:
            agg_dict.update({agg_column: lambda x: x.iloc[0]})
        else:
            agg_dict.update({agg_column: 'sum'})

    return data_frame.groupby(columns_to_groupby).agg(agg_dict)


def group_by_vaccines(data_frame):
    agg_dict = {}
    columns_to_groupby = ['data_point', 'region', 'vac_interval_group']
    for agg_column in data_frame.columns:
        if agg_column == 'vaccine':
            agg_dict.update({agg_column: lambda x: 'AllVaccines'})
        elif agg_column in columns_to_groupby:
            agg_dict.update({agg_column: lambda x: x.iloc[0]})
        else:
            agg_dict.update({agg_column: 'sum'})

    return data_frame.groupby(columns_to_groupby).agg(agg_dict)


def add_aggregated_data(data_frame):
    grouped_subjects = group_by_subjects(data_frame)
    grouped_vaccines = group_by_vaccines(pd.concat([data_frame, grouped_subjects]))
    grouped_df = pd.concat([data_frame, grouped_subjects, grouped_vaccines])
    grouped_df.sort_values(by=['data_point', 'region', 'vac_interval_group', 'vaccine'], inplace=True)
    grouped_df.reset_index(inplace=True, drop=True)
    return grouped_df

