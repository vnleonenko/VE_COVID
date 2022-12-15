from dash.exceptions import PreventUpdate
from dash import Dash, Input, Output
import dash_bootstrap_components as dbc

import sys
import time as t
import numpy as np
import pandas as pd

from database_connector import MSSQL
from mobile_layout import make_mobile_layout
from utils import get_subjects, reformat_date, get_strain_data

from graphs import plot_vertical_bar_chart, plot_horizontal_bar_chart, plot_int_bar_chart
from graphs import plot_pie_chart, plot_int_bar_chart2
from graphs import plot_choropleth_map


geojson_path = r'data/map_data/subject_borders_of_russia.json'
subjects = get_subjects(geojson_path)
strain_data = get_strain_data('data/strains/20221020-MH93845-490.csv')

vaccines_dict = {'Все вакцины': 'AllVaccines',
                 'Спутник V': 'SputnikV',
                 'Спутник Лайт': 'SputnikLite',
                 'ЭпиВак': 'EpiVacCorona',
                 'КовиВак': 'CoviVac'}

title_cases = {'zab': 'симптоматического',
               'hosp': 'госпитализации с',
               'severe': 'тяжелого течения',
               'death': 'летального исхода от'}

age_postfixes = {'18-59': '_18_59',
                 '60+': '_60',
                 '18+': '_total'}

age_groups = {'18-59': 'от 18 до 59 лет',
              '60+': 'от 60 лет и старше',
              '18+': 'от 18 лет и старше'}


with MSSQL() as mssql:
    int_ve_df = mssql.extract_int_ve(ages_split=False)
    int_ages_ve_df = mssql.extract_int_ve(ages_split=True)
    general_ve_df = mssql.extract_general_ve()
    months = reformat_date(general_ve_df['data_point'].unique(), delimiter='_')


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
           meta_tags=[{'name': 'viewport', 'content': "width=device-width, "
                                                      "initial-scale=1, maximum-scale=1, user-scalable=no"}])
server = app.server
app.layout = make_mobile_layout(months)


@app.callback(
    Output('bar_chart_v', 'figure'),
    Output('bar_chart_h', 'figure'),
    Input('subject', 'value'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value'),
    Input('month_year', 'value')
)
def update_bar_chart(subject, vac_type, case, age, date_ru):
    general_ve_chart = general_ve_df[general_ve_df['region'] == subject]

    data_points = general_ve_chart['data_point'].apply(lambda x: x.split('_')[0])

    case_postfix = case
    age_postfix = age_postfixes[age]
    column = 've_' + case_postfix + age_postfix
    ci_high_title = 'cih_' + case_postfix + age_postfix
    ci_low_title = 'cil_' + case_postfix + age_postfix
    vaccine = vaccines_dict[vac_type]

    chart_data_v = general_ve_chart[general_ve_chart['vaccine'] == vaccine]
    x_v = pd.to_datetime(data_points, format='%Y.%m')
    y_v = chart_data_v[column]
    ci = (y_v - chart_data_v[ci_low_title], chart_data_v[ci_high_title] - y_v)
    title_text_v = f'ЭВ в отношении предотвращения {title_cases[case]} COVID-19 <br>({vac_type},' \
                   f' {age_groups[age]}, {subject})'
    bar_chart_v = plot_vertical_bar_chart(x=x_v, y=y_v, ci=ci, title_text=title_text_v)

    date_en = reformat_date([date_ru], to_numeric=True)[0]
    x_h = general_ve_chart[general_ve_chart['data_point'].str.contains(date_en)][column]
    y_h = general_ve_chart[general_ve_chart['data_point'].str.contains(date_en)]['vaccine'].tolist()
    vaccines_reversed_dict = {v: k for k, v in vaccines_dict.items()}
    y_h = [vaccines_reversed_dict[y] for y in y_h]
    title_text_h = f'ЭВ в отношении предотвращения<br>{title_cases[case]} COVID-19<br>({age_groups[age]},' \
                   f' {date_ru}, {subject})'
    bar_chart_h = plot_horizontal_bar_chart(x_h, y_h, title_text_h)

    return [bar_chart_v, bar_chart_h]


@app.callback(
    Output('map', 'figure'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value'),
    Input('month_year', 'value'),
    Input('map-checklist', 'value')
)
def update_map(vac_type, case, age, date_ru, update_fig):
    map_data = general_ve_df[general_ve_df['region'] != 'РФ']
    map_data = map_data.fillna(0.0, axis=1)

    if len(update_fig) == 0:
        raise PreventUpdate
    age_postfix = age_postfixes[age]

    column = 've_' + case + age_postfix
    date_en = reformat_date([date_ru], to_numeric=True, delimiter='.')[0]
    map_data = map_data.query(f'vaccine == "{vaccines_dict[vac_type]}"')
    map_data = map_data[map_data['data_point'].str.contains(date_en)]
    map_data.rename(columns={'region': 'name'}, inplace=True)
    title_text = f'ЭВ в отношении предотвращения {title_cases[case]} COVID-19<br>({vac_type}, {age_groups[age]},' \
                 f' {date_ru})'
    map_figure = plot_choropleth_map(subjects, map_data, column, 'name', title_text)

    return map_figure


@app.callback(
    Output('interval_bar_chart', 'figure'),
    Input('subject', 'value'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value'),
    Input('month_year_int', 'value')
)
def update_interval_bar_chart(subject, vac_type, case, age, dates_list):
    converted_dates = sorted(reformat_date(dates_list, to_numeric=True, delimiter='.'), key=lambda x: x.split("."))
    chart_data = int_ve_df.query(f'region == "{subject}" & vaccine == "{vaccines_dict[vac_type]}" &'
                             f'age_group == "{age}"')
    chart_data = chart_data.replace([None, np.nan, np.inf], 0)
    title_text = f'ЭВ в отношении предотвращения {title_cases[case]} COVID-19<br>({vac_type}, {age_groups[age]}, ' \
                 f'{subject})'
    fig = plot_int_bar_chart(chart_data, converted_dates, case, title_text)

    return fig


@app.callback(
    Output('interval_bar_chart2', 'figure'),
    Input('subject', 'value'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_slider', 'value'),
    Input('month_year_int', 'value')
)
def update_int_bar_chart2(subject, vac_type, case, age, dates):
    ages_dict = {0: '20-29', 1: '30-39', 2: '40-49',
                 3: '50-59', 4: '60-69', 5: '70-79', 6: '80+'}

    data = int_ages_ve_df.query(f'region == "{subject}" & vaccine == "{vaccines_dict[vac_type]}" &'
                             f'age_group == "{ages_dict[age]}"')

    converted_dates = sorted(reformat_date(dates, to_numeric=True, delimiter='.'), key=lambda x: x.split("."))
    title_text = f'ЭВ в отношении предотвращения {title_cases[case]} COVID-19<br>({vac_type}, ' \
                 f'{ages_dict[age]} лет, {subject})'
    fig = plot_int_bar_chart2(data, converted_dates, case, title_text)
    return fig


@app.callback(
    Output('pie-chart', 'figure'),
    Output('strain_month_year', 'options'),
    Input('strain_month_year', 'value'),
    Input('subject', 'value')
)
def update_pie_chart(date, subject):
    strain_dates = strain_data['collection_date'].unique()
    subject_en = ''
    if subject == 'РФ':
        subject_en = 'Russian Federation'
    elif subject == 'г. Санкт-Петербург':
        subject_en = 'Saint Petersburg'
    elif subject == 'Московская область':
        subject_en = 'Moscow'

    pie_chart_data = strain_data.query(f'collection_date == "{date}" & subject == "{subject_en}"')

    strain_dates_ru = reformat_date(strain_dates.tolist(), delimiter='-')
    date_options = [{'label': l, 'value': v} for l, v in zip(strain_dates_ru, strain_dates)]

    date_ru = reformat_date([date], delimiter='-')
    title_text = f'Соотношение циркулирующих штаммов COVID-19 ({subject}, {date_ru[0]})'
    fig = plot_pie_chart(pie_chart_data, title_text)

    return [fig, date_options]


if __name__ == '__main__':
    app.run_server(debug=True)
