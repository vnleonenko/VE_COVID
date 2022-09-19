from copy import deepcopy

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output

from layout import make_layout
from utils import get_subjects, parse_files, get_graph_data
from graphs import plot_choropleth_map
from graphs import plot_vertical_bar_chart, plot_horizontal_bar_chart


geojson_path = r'./data/map_data/subjects_borders_of_russia.json'
subjects = get_subjects(geojson_path)

csv_folder_path = r'./data/input_csv_files'
data = parse_files(csv_folder_path)
bar_chart_data = get_graph_data(data)

ru_en_month = dict(январь='01', февраль='02', март='03',
                   апрель='04', май='05', июнь='06',
                   июль='07', август='08', сентябрь='09',
                   октябрь='10', ноябрь='11', декабрь='12')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server_v2 = app.server
app.layout = make_layout()


@app.callback(
    Output('store-data', 'data'),
    Output('store-chart-data', 'data'),
    Input('age_group', 'value'),
)
def update_store(_):
    temp_dict = deepcopy(data)
    for key, value_dict in temp_dict.items():
        for date, item_df in value_dict.items():
            value_dict[date] = item_df.to_dict('records')

    temp_chart_data = deepcopy(bar_chart_data)
    temp_chart_data = temp_chart_data.to_dict('records')

    return [temp_dict, temp_chart_data]


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
    stored_data['date'] = pd.to_datetime(stored_data['date'], dayfirst=True, infer_datetime_format=True)
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

    column = case_prefix + '_ve' + age_prefix
    ci_high_title = case_prefix + '_cih' + age_prefix
    ci_low_title = case_prefix + '_cil' + age_prefix
    chart_data_v = stored_data[stored_data['vaccine'] == vac_type]
    x_v = chart_data_v['date']
    y_v = chart_data_v[column]
    ci = (y_v - chart_data_v[ci_low_title], chart_data_v[ci_high_title] - y_v)
    title_text_v = f'ЭВ в отношении предотвращения {title_case} COVID-19 <br>({vac_type}, {age})'
    bar_chart_v = plot_vertical_bar_chart(x=x_v, y=y_v, ci=ci, title_text=title_text_v)

    month, year, _ = date_ru.split(" ")
    date_en = f'{year}-{ru_en_month[month]}-15'
    x_h = stored_data[stored_data['date'] == date_en][column]
    y_h = stored_data[stored_data['date'] == date_en]['vaccine']
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

    for vaccine, value_dict in stored_data.items():
        for date, item_list in value_dict.items():
            value_dict[date] = pd.DataFrame(item_list)

    column = case_prefix + '_ve' + age_prefix
    map_data = stored_data[vac_type][date_ru].iloc[:-1, :]
    title_text = f'ЭВ в отношении предотвращения {title_case} COVID-19<br>({vac_type}, {age}, {date_ru})'
    map_figure = plot_choropleth_map(subjects, map_data, column, 'name', title_text)

    return map_figure


if __name__ == '__main__':
    app.run_server(debug=True)
