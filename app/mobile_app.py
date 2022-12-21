from dash.exceptions import PreventUpdate
from dash import Dash, Input, Output
import dash_bootstrap_components as dbc

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

cases = {'zab': 1, 'hosp': 2, 'severe': 3, 'death': 4}
vaccine_ids = {'AllVaccines': 99,
                 'SputnikV': 1,
                 'SputnikLite': 5,
                 'EpiVacCorona': 3,
                 'CoviVac': 4}

temp_age_dict = {'18-59': 18, '60+': 60, '18+': 99}


def initial_data_extraction(**kwargs):
    subject_value = kwargs.get('subject_value')
    vaccine_value = kwargs.get('vaccine_value')
    age_value = kwargs.get('age_value')
    case_value = kwargs.get('case_value')

    with MSSQL() as mssql:
        # int_ve_df = mssql.extract_int_ve(ages_split=False)
        # int_ages_ve_df = mssql.extract_int_ve(ages_split=True)
        subject_id = mssql.cursor.execute(f'''select reg_id from dbo.REG_IDS 
                                          where region = '{subject_value}' ''').fetchone()[0]
        vaccine_id = vaccine_ids[vaccine_value]
        case_id = cases[case_value]
        age_id = temp_age_dict[age_value]
        query = f'''
        select sq1.data_point, sq1.region, sq1.age_group, sq1.vaccine,
        sum(sq1.ve_zab) as ve_zab, sum(sq1.cil_zab) as cil_zab, sum(sq1.cih_zab) as cih_zab,
        sum(sq1.ve_hosp) as ve_hosp, sum(sq1.cil_hosp) as cil_hosp, sum(sq1.cih_hosp) as cih_hosp,
        sum(sq1.ve_severe) as ve_severe, sum(sq1.cil_severe) as cil_severe, sum(sq1.cih_severe) as cih_severe,
        sum(sq1.ve_death) as ve_death, sum(sq1.cil_death) as cil_death, sum(sq1.cih_death) as cih_death
        from
        (select data_point, 
        case when reg_id = {subject_id} then '{subject_value}' end as region,
        case when age_id = {age_id} then '{age_value}' end as age_group,
        case when vaccine_id = {vaccine_id} then '{vaccine_value}' end as vaccine,
        
        case when case_type = 1 then ve end as ve_zab,
        case when case_type = 1 then cil end as cil_zab,
        case when case_type = 1 then cih end as cih_zab,
        
        case when case_type = 2 then ve end as ve_hosp,
        case when case_type = 2 then cil end as cil_hosp,
        case when case_type = 2 then cih end as cih_hosp,
        
        case when case_type = 3 then ve end as ve_severe,
        case when case_type = 3 then cil end as cil_severe,
        case when case_type = 3 then cih end as cih_severe,
        
        case when case_type = 4 then ve end as ve_death,
        case when case_type = 4 then cil end as cil_death,
        case when case_type = 4 then cih end as cih_death             
        from dbo.VE_CI 
        where reg_id = {subject_id} and vaccine_id = {vaccine_id} and age_id = {age_id}
        ) as sq1
        group by sq1.data_point, sq1.region, sq1.vaccine, sq1.age_group'''

        columns = mssql._get_columns()
        columns.remove('vac_interval_group')
        general_ve_df = mssql._query_to_df(query, columns)
        months = reformat_date(general_ve_df['data_point'].unique(), delimiter='_')
    return general_ve_df, months


initial_values = {'subject_value': 'РФ', 'vaccine_value': 'SputnikV',
                  'age_value': '18-59', 'case_value': 'zab'}
general_ve_df, months = initial_data_extraction(**initial_values)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
           meta_tags=[{'name': 'viewport', 'content': "width=device-width, "
                                                      "initial-scale=1, maximum-scale=1, user-scalable=no"}])
server = app.server
app.layout = make_mobile_layout(months, initial_values)


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
    '''print(subject, vac_type, case, age)
    vaccine_id, age_id = vaccine_ids[vac_type], int(age[:2])

    with MSSQL() as mssql:
        query = f"""select * from dbo.VE_CI
                where vaccine_id = {vaccine_id} and age_id = {age_id}"""
        general_ve_df = mssql.cursor.execute(query).fetchall()
        months = reformat_date(general_ve_df['data_point'].unique(), delimiter='_')'''

    general_ve_chart = general_ve_df[general_ve_df['region'] == subject]
    column = 've_' + case
    ci_high_title = 'cih_' + case
    ci_low_title = 'cil_' + case

    chart_data_v = general_ve_chart[general_ve_chart['vaccine'] == vac_type]
    data_points = chart_data_v['data_point'].apply(lambda x: x.split('_')[0])
    x_v = pd.to_datetime(data_points)
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
    print(map_data)

    if len(update_fig) == 0:
        raise PreventUpdate
    age_postfix = age_postfixes[age]

    column = 've_' + case
    date_en = reformat_date([date_ru], to_numeric=True, delimiter='.')[0]
    map_data = map_data.query(f'vaccine == "{vac_type}"')
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
    with MSSQL() as mssql:
        int_ve_df = mssql.extract_int_ve(subject, age, vac_type, ages_split=False)

    converted_dates = sorted(reformat_date(dates_list, to_numeric=True, delimiter='.'), key=lambda x: x.split("."))
    chart_data = int_ve_df.replace([None, np.nan, np.inf], 0)
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

    with MSSQL() as mssql:
        int_ages_ve_df = mssql.extract_int_ve(subject, ages_dict[age], vac_type, ages_split=True)

    converted_dates = sorted(reformat_date(dates, to_numeric=True, delimiter='.'), key=lambda x: x.split("."))
    title_text = f'ЭВ в отношении предотвращения {title_cases[case]} COVID-19<br>({vac_type}, ' \
                 f'{ages_dict[age]} лет, {subject})'
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
