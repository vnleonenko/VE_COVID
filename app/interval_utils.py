from .utils import parse_csv
import pandas as pd
import pyodbc
import os


def get_interval_data(folder_path):
    df_list = []
    for file_path in os.listdir(folder_path):
        df_list.append(parse_csv(os.path.join(folder_path, file_path), encoding='cp1251'))
    df = pd.concat(df_list, ignore_index=True)
    df.reset_index(drop=True, inplace=True)
    df.iloc[:, :4] = df.iloc[:, :4].astype('category')
    df.iloc[:, 4:] = df.iloc[:, 4:].astype('float32')
    return df


def get_months(folder_path):
    dates = []
    months_dict = {'01': 'январь', '02': 'февраль', '03': 'март',
                   '04': 'апрель', '05': 'май', '06': 'июнь',
                   '07': 'июль', '08': 'август', '09': 'сентябрь',
                   '10': 'октябрь', '11': 'ноябрь', '12': 'декабрь'}
    for file_name in os.listdir(folder_path):
        date = file_name.split('_')
        year, month = date[0], date[1]
        dates.append(f'{months_dict[month]} {year} г.')
    return dates


def convert_date_format(date_list):
    months_dict = {'январь': '01', 'февраль': '02', 'март': '03',
                   'апрель': '04', 'май': '05', 'июнь': '06',
                   'июль': '07', 'август': '08', 'сентябрь': '09',
                   'октябрь': '10', 'ноябрь': '11', 'декабрь': '12'}
    converted_dates = []
    for date in date_list:
        month, year, _ = date.split(" ")
        converted_dates.append(f'{year}.{months_dict[month]}')
    return converted_dates


def connect_to_db():
    server = 'tcp:db.influenza.spb.ru,1984'
    database = 'VE'
    username = 've_access'
    password = 'VE@niiGrippa4$'
    cnxn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};'
                          'SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password,
                          autocommit=True)
    return cnxn, cnxn.cursor()


def query_to_df(query, cursor, columns):
    query_res = list(map(list, cursor.execute(query).fetchall()))
    return pd.DataFrame(query_res, columns=columns)

