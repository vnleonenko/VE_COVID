import json
import pandas as pd
from database_connector import MSSQL


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
            date = date.split(delimiter)
            if len(date) == 2 and '.' in date[0]:
                year, month = date[0].split('.')
            else:
                year, month = date
            result.append(f'{months_dict[month]} {year} г.')
    return result


def compute_ve(pcv, ppv):
    ve_columns = ['data_point', 'region', 'vac_interval_group', 'vaccine',
                  've_zab_18_59', 've_hosp_18_59', 've_severe_18_59', 've_death_18_59',
                  've_zab_60', 've_hosp_60', 've_severe_60', 've_death_60',
                  've_zab_total', 've_hosp_total', 've_severe_total', 've_death_total']
    ve_df = pd.DataFrame(columns=ve_columns)
    merged_pcv_ppv = ppv.merge(pcv, on=['data_point', 'region', 'vac_interval_group', 'vaccine'],
                               how='outer')
    for ve_column in ve_columns:
        if ve_column in pcv.columns and ve_column in ppv.columns:
            ve_df[ve_column] = merged_pcv_ppv[ve_column]
        else:
            if '18_59' in ve_column:
                age = '_18_59'
            elif '60' in ve_column:
                age = '_60'
            else:
                age = '_total'
            case = ve_column.split('_')[1]
            factor_pcv = merged_pcv_ppv['pcv_' + case + age] / (1 - merged_pcv_ppv['pcv_' + case + age])
            factor_ppv = (1 - merged_pcv_ppv['ppv' + age]) / merged_pcv_ppv['ppv' + age]
            ve_df[ve_column] = round(1 - (factor_pcv * factor_ppv), 5)

    return ve_df


def calc_virus_ratio(virus_titles: list):
    virus_types_ratio = {}
    for title in virus_titles:
        if title in list(virus_types_ratio.keys()):
            virus_types_ratio[title] += 1
        else:
            virus_types_ratio[title] = 1
    virus_types_ratio = {k: round(v / len(virus_titles), 5) for k, v in virus_types_ratio.items()}
    return virus_types_ratio


def get_strain_data(csv_path):
    strain_data = pd.read_csv(csv_path)
    filtered_data = strain_data.loc[:, ['location', 'collection_date',
                                 'pango_lineage', 'pangolin_version', 'variant',
                                 'latitude', 'longitude', 'city', 'subject', 'district']]

    filtered_data['collection_date'] = filtered_data['collection_date'].map(lambda x: x.rsplit('-', 1)[0])
    grouped_data = filtered_data.groupby(['collection_date', 'city',
                                          'subject', 'district']).agg({'location': lambda x: x.iloc[0],
                                                                       'pango_lineage': lambda x: list(x),
                                                                       'pangolin_version': lambda x: list(x),
                                                                       'variant': lambda x: x.iloc[0],
                                                                       'latitude': lambda x: x.iloc[0],
                                                                       'longitude': lambda x: x.iloc[0]})
    grouped_data.reset_index(inplace=True)
    agg_rf = grouped_data.groupby('collection_date', as_index=False).agg({'city': lambda x: 'Russia',
                                                          'subject': lambda x: 'Russian Federation',
                                                          'district': lambda x: '--',
                                                          'location': lambda x: '--',
                                                          'pango_lineage': lambda x: sum(x, []),
                                                          'pangolin_version': lambda x: sum(x, []),
                                                          'variant': lambda x: x.iloc[0],
                                                          'latitude': lambda x: '--',
                                                          'longitude': lambda x: '--'})
    grouped_data = pd.concat([grouped_data, agg_rf])
    grouped_data.reset_index(inplace=True, drop=True)
    grouped_data.sort_values(by='collection_date', inplace=True)
    grouped_data['pango_lineage'] = grouped_data['pango_lineage'].apply(calc_virus_ratio)
    grouped_data['pangolin_version'] = grouped_data['pangolin_version'].apply(calc_virus_ratio)
    return grouped_data


def get_months():
    with MSSQL() as mssql:
        month_query = f'''select distinct(data_point) from dbo.VE_TEST
                      where data_point not like '%[B]%' '''
        # and data_point not like '%[X]%'
        months_en = mssql.cursor.execute(month_query).fetchall()
        months_en = sorted([t[0] for t in months_en], key=lambda x: x.split('_'))
        months_ru = reformat_date(months_en, delimiter='_')
    return months_ru
