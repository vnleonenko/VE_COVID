from dash.exceptions import PreventUpdate
from dash import Dash, Input, Output
import dash_bootstrap_components as dbc

import numpy as np
import pandas as pd

from database_connector import MSSQL
from mobile_layout import make_mobile_layout
from utils import get_subjects, reformat_date, get_strain_data, get_months

from graphs import plot_vertical_bar_chart, plot_horizontal_bar_chart, plot_int_bar_chart
from graphs import plot_pie_chart, plot_int_bar_chart2
from graphs import plot_choropleth_map


geojson_path = r'data/map_data/subject_borders_of_russia.json'
subjects = get_subjects(geojson_path)
strain_data = get_strain_data('data/strains/20221020-MH93845-490.csv')

vaccines_dict = {'AllVaccines': 'Все вакцины',
                 'SputnikV': 'Спутник V',
                 'SputnikLite': 'Спутник Лайт',
                 'EpiVacCorona': 'ЭпиВак',
                 'CoviVac': 'КовиВак'}

cases = {'zab': 'симптоматического',
         'hosp': 'госпитализации с',
         'severe': 'тяжелого течения',
         'death': 'летального исхода от'}

age_groups = {'18-59': 'от 18 до 59 лет',
              '60+': 'от 60 лет и старше',
              '18+': 'от 18 лет и старше'}


initial_values = {'subject_value': 'РФ', 'vaccine_value': 'SputnikV',
                  'age_value': '18-59', 'case_value': 'zab'}

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
           meta_tags=[{'name': 'viewport', 'content': "width=device-width, "
                       "initial-scale=1, maximum-scale=1, user-scalable=no"}])
server = app.server
app.layout = make_mobile_layout(get_months(), initial_values)


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
    with MSSQL() as mssql:
        general_ve_df = mssql.extract_ve(age, age_groups=3, vac_intervals=1)

    # general_ve_df = general_ve_df.replace([None, np.nan, np.inf], 0)
    general_ve_chart = general_ve_df[general_ve_df['region'] == subject]
    column = 've_' + case
    ci_high_title = 'cih_' + case
    ci_low_title = 'cil_' + case

    chart_data_v = general_ve_chart[general_ve_chart['vaccine'] == vac_type]
    data_points = chart_data_v['data_point'].apply(lambda x: x.split('_')[0])
    x_v = pd.to_datetime(data_points)
    y_v = chart_data_v[column]
    ci = (y_v - chart_data_v[ci_low_title], chart_data_v[ci_high_title] - y_v)
    title_text_v = f'ЭВ в отношении предотвращения {cases[case]} COVID-19 <br>' \
                   f'({vaccines_dict[vac_type]}, {age_groups[age]}, {subject})'
    bar_chart_v = plot_vertical_bar_chart(x=x_v, y=y_v, ci=ci, title_text=title_text_v)

    date_en = reformat_date([date_ru], to_numeric=True)[0]
    x_h = general_ve_chart[general_ve_chart['data_point'].str.contains(date_en)][column]
    y_h = general_ve_chart[general_ve_chart['data_point'].str.contains(date_en)]['vaccine'].tolist()
    y_h = [vaccines_dict[y] for y in y_h]
    title_text_h = f'ЭВ в отношении предотвращения<br>{cases[case]} COVID-19<br>' \
                   f'({age_groups[age]}, {date_ru}, {subject})'
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
    with MSSQL() as mssql:
        general_ve_map_df = mssql.extract_ve(age, vac_type, age_groups=3, vac_intervals=1)
    map_data = general_ve_map_df[general_ve_map_df['region'] != 'РФ']
    map_data = map_data.replace([None, np.nan, np.inf], 0)

    if len(update_fig) == 0:
        raise PreventUpdate

    column = 've_' + case
    date_en = reformat_date([date_ru], to_numeric=True, delimiter='.')[0]
    map_data = map_data.query(f'vaccine == "{vac_type}"')
    map_data = map_data[map_data['data_point'].str.contains(date_en)]
    map_data.rename(columns={'region': 'name'}, inplace=True)
    title_text = f'ЭВ в отношении предотвращения {cases[case]} COVID-19<br>' \
                 f'({vaccines_dict[vac_type]}, {age_groups[age]}, {date_ru})'
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
    with MSSQL() as mssql:
        int_ve_df = mssql.extract_ve(age, vac_type, subject=subject, age_groups=3, vac_intervals=6)

    converted_dates = sorted(reformat_date(dates_list, to_numeric=True, delimiter='.'), key=lambda x: x.split("."))
    chart_data = int_ve_df.replace([None, np.nan, np.inf], 0)
    title_text = f'ЭВ в отношении предотвращения {cases[case]} COVID-19<br>' \
                 f'({vaccines_dict[vac_type]}, {age_groups[age]}, {subject})'
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

    with MSSQL() as mssql:
        int_ages_ve_df = mssql.extract_ve(ages_dict[age], vac_type, subject=subject, age_groups=7, vac_intervals=6)

    converted_dates = sorted(reformat_date(dates, to_numeric=True, delimiter='.'), key=lambda x: x.split("."))
    title_text = f'ЭВ в отношении предотвращения {cases[case]} COVID-19<br>' \
                 f'({vaccines_dict[vac_type]}, {ages_dict[age]} лет, {subject})'
    fig = plot_int_bar_chart2(int_ages_ve_df, converted_dates, case, title_text)
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
