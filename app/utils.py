import datetime
import json
import os

import pandas as pd


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
        '''name = subject['properties']['name']
        geometry = subject['geometry']
        id = subject['id']
        subjects.append({'id': id, 'properties': {'name': name},
                         'geometry': geometry})'''

    json_data['features'] = sorted(json_data['features'], key=lambda x: x['properties']['name'])
    return json_data


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
        df_.fillna(0.0, axis=1, inplace=True)
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

    res_df = res_df.sort_values(['date', 'vaccine'])
    res_df.reset_index(drop=True, inplace=True)

    return res_df


def get_months(csv_folder_path):
    months = {}
    en_ru_month = {'01': 'январь', '02': 'февраль', '03': 'март',
                   '04': 'апрель', '05': 'май', '06': 'июнь',
                   '07': 'июль', '08': 'август', '09': 'сентябрь',
                   '10': 'октябрь', '11': 'ноябрь', '12': 'декабрь'}
    files_names = os.listdir(csv_folder_path)
    for file_name in files_names:
        if file_name.endswith('.csv') and file_name != 'synthetic_data.csv':
            year_month = file_name.split('_')[0]
            if year_month not in list(months.keys()):
                year, month = year_month.split('.')
                month_year_ru = en_ru_month[month] + ' ' + year + ' г.'
                months.update({month_year_ru: file_name})
    return months


if __name__ == '__main__':
    geojson_path = r"data/map_data/admin_level_4_copy.geojson"
    sub = get_subjects(geojson_path)
    print(sub['features'][0]['properties'].keys())

