import os
import json
import folium
import pandas as pd
from datetime import date


def parse_csv(file_path, encoding='utf-8'):
    data = pd.read_csv(file_path, encoding=encoding, header=0, delimiter=';', decimal='.')
    return data


def parse_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as jfile:
        return json.load(jfile)


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


def merge_geo_data(file_path, df):
    geojson = get_subjects(file_path)
    df_columns = ['zab_ve_18_59_R', 'zab_ve_60_R', 'zab_ve_total_R',
               'st_ve_18_59_R', 'st_ve_60_R', 'st_ve_total_R',
               'tyazh_ve_18_59_R', 'tyazh_ve_60_R', 'tyazh_ve_total_R',
               'sm_ve_18_59_R', 'sm_ve_60_R', 'sm_ve_total_R']
    for feature in geojson['features']:
        subject_name = feature['properties']['name']
        df_row = df[df['region'] == subject_name]
        for column in df_columns:
            feature['properties'][column] = df_row[column].item()
    return geojson

'''
def read_csv_files(folder_path):
    csv_files = {}
    en_ru_month = {'JAN': 'январь', 'FEB': 'февраль', 'MAR': 'март',
                   'APR': 'апрель', 'MAY': 'май', 'JUN': 'июнь',
                   'JUL': 'июль', 'AUG': 'август', 'SEP': 'сентябрь',
                   'OCT': 'октябрь', 'NOV': 'ноябрь', 'DEC': 'декабрь'}
    files_names = os.listdir(folder_path)
    for file_name in files_names:
        if file_name.endswith('.csv') and file_name != 'synthetic_data.csv':
            month_year = file_name.split('-')[0]
            month_year_ru = en_ru_month[month_year[:-2]] + " 20" + month_year[-2:] + ' г.'
            csv_files.update({month_year_ru: file_name})
    return csv_files
'''


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


def create_map(map_data, column_title, geojson_path, map_path):
    merged_map_data = merge_geo_data(map_data, geojson_path)

    longitude, latitude = 70.751244, 110.618423

    map_figure = folium.Map(location=[longitude, latitude], zoom_start=3, tiles=None, prefer_canvas=True)
    folium.TileLayer('openstreetmap', overlay=True, name="View in Light Mode", control=False).add_to(map_figure)

    create_choropleth_map(map_figure, merged_map_data, column_title)

    folium.LayerControl().add_to(map_figure)
    map_figure.save(map_path)


def create_choropleth_map(original_map, geo_data, column_title):
    fg = folium.FeatureGroup(name='ve', overlay=False).add_to(original_map)

    folium.Choropleth( geo_data=geo_data,
                       name='Choropleth',
                       data=geo_data,
                       columns=['name', column_title],
                       key_on='feature.properties.name',
                       fill_color='PuBu',
                       nan_fill_color="White",
                       fill_opacity=0.7,
                       line_opacity=0.2,
                       legend_name='Vaccination efficiency',
                       highlight=True,
                       overlay=False,
                       line_color='black').geojson.add_to(fg)

    folium.features.GeoJson(data=geo_data, name='Choropleth',
                            smooth_factor=2,
                            style_function=lambda x: {'color': 'black', 'fillColor': 'transparent', 'weight': 0.1},
                            tooltip=folium.features.GeoJsonTooltip(
                                fields=['name', column_title],
                                aliases=["Субъект: ", "ЭВ: "],
                                localize=True,
                                sticky=False,
                                labels=True,
                                style=""" background-color: #F0EFEF;
                                          border: 0px solid black;
                                          border-radius: 2px;
                                          box-shadow: 1px; """,
                                max_width=800),
                            highlight_function=lambda x: {'weight': 1, 'fillColor': 'grey'}
                            ).add_to(original_map)
    # original_map.keep_in_front(geojson_map)


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
        info_date = date(*info_date, 15)
        ve_russia.insert(0, info_date)
        ve_russia.remove('РФ')
        if vac_type not in list(ve.keys()):
            ve[vac_type] = [ve_russia]
        else:
            ve[vac_type].append(ve_russia)
    ve = {k: list_to_df(v) for k, v in ve.items()}

    return ve


if __name__ == '__main__':
    csv_path = r'C:\Users\User\PycharmProjects\ve_dashboard\VE_visualization\input_csv_files\FEB22-01-07-2022.csv'
    df = parse_csv(csv_path)
    df = df.fillna(0)
    geojson_path = r'/VE_COVID/map_data/admin_level_4_copy.geojson'
    geojson_data = merge_geo_data(geojson_path, df)
    print(geojson_data['features'][0])

