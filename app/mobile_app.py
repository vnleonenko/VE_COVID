from copy import deepcopy
import random as rnd
import numpy as np

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output

from mobile_layout import make_mobile_layout
from utils import get_subjects, parse_files, get_graph_data, parse_csv
from interval_utils import get_interval_data, convert_date_format

from graphs import plot_choropleth_map
from graphs import plot_vertical_bar_chart, plot_horizontal_bar_chart
import plotly.graph_objects as go


geojson_path = r'./data/map_data/subjects_borders_of_russia.json'
subjects = get_subjects(geojson_path)

general_ve_path = './data/input_csv_files/general/general_ve.csv'
general_ve = parse_csv(general_ve_path, encoding='cp1251')
bar_chart_general_ve = general_ve[general_ve['region'] == 'РФ']
map_data = general_ve[general_ve['region'] != 'РФ']
ru_en_month = dict(январь='01', февраль='02', март='03',
                   апрель='04', май='05', июнь='06',
                   июль='07', август='08', сентябрь='09',
                   октябрь='10', ноябрь='11', декабрь='12')
en_ru_month = {v: k for k, v in ru_en_month.items()}

month_list = []
for data_point in pd.unique(bar_chart_general_ve['data_point']):
    data_point = data_point.split('_')[0]
    year, month = data_point.split('.')
    month_list.append(f'{en_ru_month[month]} {year} г.')


int_data_folder_path = './data/input_csv_files/interval'
int_map_data = get_interval_data(int_data_folder_path)
interval_data = int_map_data.query('region=="РФ"')
vaccines_ru_en = {'Все вакцины': 'AllVaccines', 'Спутник V': 'SputnikV', 'Спутник Лайт': 'SputnikLite',
                  'ЭпиВак': 'EpiVacCorona', 'КовиВак': 'CoviVac'}


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
           meta_tags=[{'name': 'viewport',
                       'content': 'width=device-width, initial-scale=0.9, maximum-scale=1.1,'
                                  'minimum-scale=0.5'}])
server_v2 = app.server
app.layout = make_mobile_layout(month_list)


@app.callback(
    Output('store-data', 'data'),
    Output('store-chart-data', 'data'),
    Input('age_group', 'value'),
)
def update_store(_):
    temp_map_data = deepcopy(map_data).to_dict('records')
    temp_chart_data = deepcopy(bar_chart_general_ve).to_dict('records')

    return [temp_map_data, temp_chart_data]


@app.callback(
    Output('bar_chart_v', 'figure'),
    Output('bar_chart_h', 'figure'),
    Input('store-chart-data', 'data'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value'),
    Input('month_year', 'value')
)
def update_bar_chart(stored_data, vac_type, case, age, date_ru):
    stored_data = pd.DataFrame(stored_data)
    stored_data['data_point'] = stored_data['data_point'].apply(lambda x: x.split('_')[0])
    stored_data['data_point'] = pd.to_datetime(stored_data['data_point'], format='%Y.%m')
    case_prefix = case
    title_case = ''
    if age == 'от 18 до 59 лет':
        age_prefix = '_18_59_R'
    elif age == 'от 60 лет и старше':
        age_prefix = '_60_R'
    else:
        age_prefix = '_total_R'
    if case == 'zab':
        title_case = 'симптоматического'
    elif case == 'st':
        title_case = 'госпитализации с'
    elif case == 'tyazh':
        title_case = 'тяжелого течения'
    elif case == 'sm':
        title_case = 'летального исхода от'

    vaccine = ''
    if vac_type == 'Все вакцины':
        vaccine = 'AllVaccines'
    elif vac_type == 'Спутник V':
        vaccine = 'SputnikV'
    elif vac_type == 'Спутник Лайт':
        vaccine = 'SputnikLite'
    elif vac_type == 'ЭпиВак':
        vaccine = 'EpiVacCorona'
    elif vac_type == 'КовиВак':
        vaccine = 'CoviVac'

    column = case_prefix + '_ve' + age_prefix
    ci_high_title = case_prefix + '_cih' + age_prefix
    ci_low_title = case_prefix + '_cil' + age_prefix
    chart_data_v = stored_data[stored_data['vaccine'] == vaccine]
    x_v = chart_data_v['data_point']
    y_v = chart_data_v[column]
    ci = (y_v - chart_data_v[ci_low_title], chart_data_v[ci_high_title] - y_v)
    title_text_v = f'ЭВ в отношении предотвращения {title_case} COVID-19 <br>({vac_type}, {age})'
    bar_chart_v = plot_vertical_bar_chart(x=x_v, y=y_v, ci=ci, title_text=title_text_v)

    month, year, _ = date_ru.split(" ")
    date_en = f'{year}-{ru_en_month[month]}-01'
    x_h = stored_data[stored_data['data_point'] == date_en][column]
    y_h = stored_data[stored_data['data_point'] == date_en]['vaccine']
    title_text_h = f'ЭВ в отношении предотвращения<br>{title_case} COVID-19<br>({age}, {date_ru})'
    bar_chart_h = plot_horizontal_bar_chart(x_h, y_h, title_text_h)

    return [bar_chart_v, bar_chart_h]


@app.callback(
    Output('map', 'figure'),
    Input('store-data', 'data'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value'),
    Input('month_year', 'value'),
)
def update_map(stored_data, vac_type, case, age, date_ru):
    stored_data = pd.DataFrame(stored_data)
    stored_data.fillna(0.0, axis=1, inplace=True)

    case_prefix = case
    title_case = ''
    age_prefix = ''

    if age == 'от 18 до 59 лет':
        age_prefix = '_18_59_R'
    elif age == 'от 60 лет и старше':
        age_prefix = '_60_R'
    else:
        age_prefix = '_total_R'

    if case == 'zab':
        title_case = 'симптоматического'
    elif case == 'st':
        title_case = 'госпитализации с'
    elif case == 'tyazh':
        title_case = 'тяжелого течения'
    elif case == 'sm':
        title_case = 'летального исхода от'

    column = case_prefix + '_ve' + age_prefix
    date_en = convert_date_format([date_ru])
    map_data = stored_data.query(f'vaccine == "{vaccines_ru_en[vac_type]}" & region != "РФ"')
    map_data = map_data[map_data['data_point'].str.contains(date_en[0])]
    map_data.rename(columns={'region': 'name'}, inplace=True)
    title_text = f'ЭВ в отношении предотвращения {title_case} COVID-19<br>({vac_type}, {age}, {date_ru})'
    map_figure = plot_choropleth_map(subjects, map_data, column, 'name', title_text)

    return map_figure


@app.callback(
    Output('interval_bar_chart', 'figure'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value'),
    Input('month_year_int', 'value'),

)
def update_interval_bar_chart(vac_type, case, age, dates_list):
    converted_dates = sorted(convert_date_format(dates_list),
                             key=lambda x: x.split("."))

    if age == 'от 18 до 59 лет':
        age_prefix = '_18_59'
    elif age == 'от 60 лет и старше':
        age_prefix = '_60'
    else:
        age_prefix = '_total'

    title_case = ''
    if case == 'zab':
        title_case = 'симптоматического'
    elif case == 'st':
        title_case = 'госпитализации с'
        case = 'hosp'
    elif case == 'tyazh':
        title_case = 'тяжелого течения'
        case = 'severe'
    elif case == 'sm':
        title_case = 'летального исхода от'
        case = 'death'

    case_prefix = case
    column = 've_' + case_prefix + age_prefix
    ci_high_title = 'cih_' + case_prefix + age_prefix
    ci_low_title = 'cil_' + case_prefix + age_prefix
    chart_data = interval_data[interval_data['vaccine'] == vaccines_ru_en[vac_type]]

    fig = go.Figure()
    vac_intervals = {'21_45_days': '21-45 дней', '45_75_days': '45-75 дней',
                     '75_90_days': '75-90 дней', '90_105_days': '90-105 дней',
                     '105_165_days': '105-165 дней', '165_195_days': '165-195 дней'}
    for data_point in converted_dates:
        date = data_point.split("_")[0].split(".")
        y = chart_data[chart_data['data_point'].str.contains(".".join(date))]
        date = ".".join(date[::-1])
        x = [[date for _ in range(len(vac_intervals))], list(vac_intervals.values())]
        y.reset_index(drop=True, inplace=True)
        y = pd.concat([y.iloc[2:, :], y.loc[:1, :]])
        y = y[[column, ci_high_title, ci_low_title]]
        cih = y[ci_high_title] - y[column]
        cil = y[column] - y[ci_low_title]
        title_text = f'ЭВ в отношении предотвращения {title_case} COVID-19<br>({vac_type}, {age})'
        color = [rnd.randint(150, 200), rnd.randint(150, 200), rnd.randint(200, 255)]
        fig.add_trace(go.Bar(x=x, y=y[column], width=0.6,
                             #marker={'color': f'rgb{color[0], color[1], color[2]}'},
                             showlegend=False,
                             error_y=dict(type='data',
                                          symmetric=False,
                                          array=cih,
                                          arrayminus=cil,
                                          width=3,
                                          thickness=1.6),
                             hovertemplate="<br> ЭВ: %{y:.1%}<br> ДИ: "
                                           "+%{error_y.array:.1%} "
                                           "/ -%{error_y.arrayminus:.1%} "
                                           "<extra></extra>"))
        fig.update_traces(marker_line_color='rgb(8,48,107)',
                          marker_line_width=1,
                          opacity=0.6)
        fig.update_yaxes(tickformat='.0%')
        fig.update_layout(autosize=False,
                          separators=',',
                          template='plotly_white',
                          margin={'l': 30, 'b': 25, 't': 90, 'r': 20},
                          title={'text': title_text, 'x': 0.5, 'y': 0.95,
                                 'xanchor': 'center', 'yanchor': 'top',
                                 'font': {'size': 15}})

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
