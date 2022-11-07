import json
import pandas as pd


def parse_csv(file_path, encoding='utf-8'):
    return pd.read_csv(file_path, encoding=encoding, header=0, delimiter=';', decimal='.')


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


def reformat_date(dates, to_numeric=False, delimiter='.'):
    months_dict = {'01': 'январь', '02': 'февраль', '03': 'март',
                   '04': 'апрель', '05': 'май', '06': 'июнь',
                   '07': 'июль', '08': 'август', '09': 'сентябрь',
                   '10': 'октябрь', '11': 'ноябрь', '12': 'декабрь'}
    inv_months_dict = {v: k for k, v in months_dict.items()}
    result = []

    for date in dates:
        if to_numeric:
            month, year, _ = date.split(" ")
            reformatted_date = ''
            if delimiter == '.':
                reformatted_date = f'{year}.{inv_months_dict[month]}'
            elif delimiter == '-':
                reformatted_date = f'{year}-{inv_months_dict[month]}-01'
            result.append(reformatted_date)
        else:
            year, month = date.split('_')[0].split('.')
            result.append(f'{months_dict[month]} {year} г.')
    return result

