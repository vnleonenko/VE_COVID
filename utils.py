import os
import json
import pandas as pd
import datetime


def parse_csv(file_path, encoding='utf-8'):
    data = pd.read_csv(file_path, encoding=encoding, header=0, delimiter=';', decimal='.')
    return data


def get_subjects(file_path):
    with open(file_path, 'r', encoding='utf-8') as jfile:
        json_data = json.load(jfile)

    redundant_items = []
    republics_list = ['Адыгея', 'Башкортостан', 'Бурятия', 'Дагестан', 'Ингушетия', 'Марий Эл', 'Мордовия', 'Алтай',
                      'Калмыкия', 'Татарстан', 'Тыва', 'Северная Осетия - Алания']
    cities = ['Москва', 'Санкт-Петербург', 'Севастополь']

    for i, subject in enumerate(json_data['features']):
        subject_name = subject['properties']['name']
        if subject_name in ['Автономна Республіка Крим', 'Севастополь', 'Сумска'] and \
                subject_name not in [item['properties']['name'] for item in redundant_items]:
            redundant_items.append(subject)
            json_data['features'].remove(subject)

    for subject in json_data['features']:
        if subject['properties']['name'] in republics_list:
            subject['properties']['name'] = 'Республика ' + subject['properties']['name']
        elif subject['properties']['name'] in cities:
            subject['properties']['name'] = 'г. ' + subject['properties']['name']
        elif subject['properties']['name'] == 'Карачаево-Черкесия':
            subject['properties']['name'] = 'Карачаево-Черкесская Республика'
        elif subject['properties']['name'] == 'Удмуртия':
            subject['properties']['name'] = 'Удмуртская Республика'
        elif subject['properties']['name'] == 'Чувашия':
            subject['properties']['name'] = 'Чувашская Республика'
        elif subject['properties']['name'] == 'Кабардино-Балкария':
            subject['properties']['name'] = 'Кабардино-Балкарская Республика'
        elif subject['properties']['name'] == 'Чеченская республика':
            subject['properties']['name'] = 'Чеченская Республика'

    json_data['features'] = sorted(json_data['features'], key=lambda x: x['properties']['name'])
    return json_data


def read_csv_files(folder_path):
    csv_files = {}
    en_ru_month = {'01': 'январь', '02': 'февраль', '03': 'март',
                   '04': 'апрель', '05': 'май', '06': 'июнь',
                   '07': 'июль', '08': 'август', '09': 'сентябрь',
                   '10': 'октябрь', '11': 'ноябрь', '12': 'декабрь'}

    files_names = os.listdir(folder_path)
    for file_name in files_names:
        if file_name.endswith('.csv') and file_name != 'synthetic_data.csv':
            year, month = file_name.split('_')[0].split('.')
            month_year_ru = en_ru_month[month] + ' ' + year + ' г.'
            csv_files.update({month_year_ru: file_name})
    return csv_files


def extract_map_data(csv_file):
    df = parse_csv(csv_file)
    columns = ['region', 'zab_ve_18_59_R', 'zab_ve_60_R', 'zab_ve_total_R',
               'st_ve_18_59_R', 'st_ve_60_R', 'st_ve_total_R',
               'tyazh_ve_18_59_R', 'tyazh_ve_60_R', 'tyazh_ve_total_R',
               'sm_ve_18_59_R', 'sm_ve_60_R', 'sm_ve_total_R']
    df = df[columns]
    sorted_df = df.sort_values(by='region')
    sorted_df.reset_index(inplace=True, drop=True)
    sorted_df.fillna(0.0, axis=1)
    sorted_df.rename(columns={'region': 'name'}, inplace=True)
    return sorted_df


def list_to_df(input_data):
    columns = ['date', 'zab_ve_18_59', 'zab_ve_18_59_R', 'zab_cil_18_59_R',
               'zab_cih_18_59_R', 'zab_ve_60', 'zab_ve_60_R', 'zab_cil_60_R',
               'zab_cih_60_R', 'zab_ve_total', 'zab_ve_total_R', 'zab_cil_total_R',
               'zab_cih_total_R', 'st_ve_18_59', 'st_ve_18_59_R', 'st_cil_18_59_R',
               'st_cih_18_59_R', 'st_ve_60', 'st_ve_60_R', 'st_cil_60_R',
               'st_cih_60_R', 'st_ve_total', 'st_ve_total_R', 'st_cil_total_R',
               'st_cih_total_R', 'tyazh_ve_18_59', 'tyazh_ve_18_59_R',
               'tyazh_cil_18_59_R', 'tyazh_cih_18_59_R', 'tyazh_ve_60',
               'tyazh_ve_60_R', 'tyazh_cil_60_R', 'tyazh_cih_60_R', 'tyazh_ve_total',
               'tyazh_ve_total_R', 'tyazh_cil_total_R', 'tyazh_cih_total_R',
               'sm_ve_18_59', 'sm_ve_18_59_R', 'sm_cil_18_59_R', 'sm_cih_18_59_R',
               'sm_ve_60', 'sm_ve_60_R', 'sm_cil_60_R', 'sm_cih_60_R', 'sm_ve_total',
               'sm_ve_total_R', 'sm_cil_total_R', 'sm_cih_total_R']

    df = pd.DataFrame(input_data, columns=columns)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, infer_datetime_format=True)
    df = df.sort_values(by='date')

    return df


def parse_files(folder_path):
    vac_data = {}
    vac_type = ''
    en_ru_month = {'01': 'январь', '02': 'февраль', '03': 'март',
                   '04': 'апрель', '05': 'май', '06': 'июнь',
                   '07': 'июль', '08': 'август', '09': 'сентябрь',
                   '10': 'октябрь', '11': 'ноябрь', '12': 'декабрь'}
    file_names = os.listdir(folder_path)

    for file_name in file_names:
        path = os.path.join(folder_path, file_name)
        df_ = parse_csv(path)
        date, unload_date, vac_ind = file_name.split('_')
        vac_ind = vac_ind[:-4]
        if vac_ind == '0':
            vac_type = 'Все вакцины'
        elif vac_ind == '1':
            vac_type = 'Спутник V'
        elif vac_ind == '3':
            vac_type = 'ЭпиВак'
        elif vac_ind == '4':
            vac_type = 'КовиВак'
        elif vac_ind == '5':
            vac_type = 'Спутник Лайт'
        else:
            print(f'vac_ind {vac_ind} is not recognized! Only 0, 1, 3, 4, 5 indices are acceptable.')

        if vac_type not in list(vac_data.keys()):
            vac_data[vac_type] = {}
        year, month = date.split('.')
        month_year_ru = en_ru_month[month] + ' ' + year + ' г.'
        insert_date = datetime.date(int(year), int(month), 15)
        df_.insert(0, 'date', insert_date)
        df_.insert(1, 'vaccine', vac_type)
        df_['date'] = pd.to_datetime(df_['date'], dayfirst=True, infer_datetime_format=True)
        df_.reset_index(inplace=True, drop=True)
        df_.fillna(0.0, axis=1)
        df_.rename(columns={'region': 'name'}, inplace=True)
        vac_data[vac_type].update({month_year_ru: df_})

    return vac_data


def get_graph_data(data):
    res_df = None
    for vac_type, df_list in data.items():
        for _, df_item in df_list.items():
            ve_russia = df_item[df_item['name'] == 'РФ']
            if res_df is None:
                res_df = ve_russia
            else:
                res_df = pd.concat([res_df, ve_russia], ignore_index=True)

    res_df = res_df.drop(['name'], axis=1)
    res_df = res_df.sort_values(['date', 'vaccine'])
    res_df.reset_index(drop=True, inplace=True)

    return res_df


'''
def parse_csv_files(folder_path):
    ve = {}
    vac_type = ''
    for file_name in os.listdir(folder_path):
        data = parse_csv(os.path.join(folder_path, file_name))
        ve_russia = data[data['region'] == 'РФ'].values[0].tolist()
        info_date, unload_date, vac_ind = file_name.split('_')
        vac_ind = vac_ind[:-4]
        if vac_ind == '0':
            vac_type = 'Все'
        elif vac_ind == '1':
            vac_type = 'Спутник V'
        elif vac_ind == '3':
            vac_type = 'ЭпиВак'
        elif vac_ind == '4':
            vac_type = 'КовиВак'
        elif vac_ind == '5':
            vac_type = 'Спутник Лайт'
        else:
            print(f'vac_ind {vac_ind} is not recognized! Only 0, 1, 3, 4, 5 indices are acceptable.')
        info_date = list(map(int, info_date.split('.')))
        info_date = datetime.date(*info_date, 15)
        ve_russia.insert(0, info_date)
        ve_russia.remove('РФ')
        if vac_type not in list(ve.keys()):
            ve[vac_type] = [ve_russia]
        else:
            ve[vac_type].append(ve_russia)
    ve = {k: list_to_df(v) for k, v in ve.items()}

    return ve
'''

