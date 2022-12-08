from dash.exceptions import PreventUpdate
from dash import Dash, Input, Output
import dash_bootstrap_components as dbc

import pandas as pd
import plotly.graph_objects as go

from database_connector import MSSQL
from mobile_layout import make_mobile_layout
from utils import get_subjects, reformat_date, get_strain_data

from graphs import plot_vertical_bar_chart, plot_horizontal_bar_chart, plot_int_bar_chart
from graphs import plot_choropleth_map


geojson_path = r'data/map_data/subject_borders_of_russia.json'
subjects = get_subjects(geojson_path)
strain_data = get_strain_data('data/strains/20221020-MH93845-490.csv')
ve_6_age_gr = pd.read_csv('../calculations/output/ve_9_age_groups_6_vac_intervals.csv',
                          encoding='cp1251', delimiter=';')

vaccines_dict = {'Все вакцины': 'AllVaccines',
                 'Спутник V': 'SputnikV',
                 'Спутник Лайт': 'SputnikLite',
                 'ЭпиВак': 'EpiVacCorona',
                 'КовиВак': 'CoviVac'}
title_cases = {'zab': 'симптоматического',
               'hosp': 'госпитализации с',
               'severe': 'тяжелого течения',
               'death': 'летального исхода от'}
age_postfixes = {'от 18 до 59 лет': '_18_59',
                 'от 60 лет и старше': '_60',
                 'от 18 лет и старше': '_total'}


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
           meta_tags=[{'name': 'viewport', 'content': "width=device-width, "
                                                      "initial-scale=1, maximum-scale=1, user-scalable=no"}])
server = app.server
app.layout = make_mobile_layout()


@app.callback(
    Output('store-chart-data', 'data'),
    Output('store-data', 'data'),
    Output('month_year', 'options'),
    Output('month_year', 'value'),
    Output('month_year_int', 'data'),
    Output('month_year_int', 'value'),
    Input('subject', 'value'),
)
def update_storage(subject):
    with MSSQL() as mssql:
        general_ve_df = mssql.extract_general_ve()
        months = reformat_date(general_ve_df['data_point'].unique(), delimiter='_')

        general_ve_map = general_ve_df[general_ve_df['region'] != 'РФ'].to_dict('records')
        general_ve_chart = general_ve_df[general_ve_df['region'] == subject].to_dict('records')

    return [general_ve_chart, general_ve_map, months, months[0], months, months[1:3]]


@app.callback(
    Output('store-int-data', 'data'),
    Input('subject', 'value'),
    Input('vaccine_type', 'value'),
)
def update_int_storage(subject, vac_type):
    vaccine = vaccines_dict[vac_type]
    with MSSQL() as mssql:
        int_ve_df = mssql.extract_int_ve(vaccine, subject).to_dict('records')

    return int_ve_df


@app.callback(
    Output('bar_chart_v', 'figure'),
    Output('bar_chart_h', 'figure'),
    Input('store-chart-data', 'data'),
    Input('subject', 'value'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value'),
    Input('month_year', 'value')
)
def update_bar_chart(stored_data, subject, vac_type, case, age, date_ru):
    stored_data = pd.DataFrame(stored_data)
    stored_data['data_point'] = stored_data['data_point'].apply(lambda x: x.split('_')[0])
    stored_data['data_point'] = pd.to_datetime(stored_data['data_point'], format='%Y.%m')

    case_postfix = case
    age_postfix = age_postfixes[age]
    column = 've_' + case_postfix + age_postfix
    ci_high_title = 'cih_' + case_postfix + age_postfix
    ci_low_title = 'cil_' + case_postfix + age_postfix
    vaccine = vaccines_dict[vac_type]

    chart_data_v = stored_data[stored_data['vaccine'] == vaccine]
    x_v = chart_data_v['data_point']
    y_v = chart_data_v[column]
    ci = (y_v - chart_data_v[ci_low_title], chart_data_v[ci_high_title] - y_v)
    title_text_v = f'ЭВ в отношении предотвращения {title_cases[case]} COVID-19 <br>({vac_type}, {age}, {subject})'
    bar_chart_v = plot_vertical_bar_chart(x=x_v, y=y_v, ci=ci, title_text=title_text_v)

    date_en = reformat_date([date_ru], to_numeric=True)[0]
    x_h = stored_data[stored_data['data_point'] == date_en][column]
    y_h = stored_data[stored_data['data_point'] == date_en]['vaccine']
    title_text_h = f'ЭВ в отношении предотвращения<br>{title_cases[case]} COVID-19<br>({age}, {date_ru}, {subject})'
    bar_chart_h = plot_horizontal_bar_chart(x_h, y_h, title_text_h)

    return [bar_chart_v, bar_chart_h]


@app.callback(
    Output('map', 'figure'),
    Input('store-data', 'data'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value'),
    Input('month_year', 'value'),
    Input('map-checklist', 'value')
)
def update_map(stored_data, vac_type, case, age, date_ru, update_fig):
    stored_data = pd.DataFrame(stored_data)
    stored_data.fillna(0.0, axis=1, inplace=True)

    if len(update_fig) == 0:
        raise PreventUpdate

    age_postfix = age_postfixes[age]

    column = 've_' + case + age_postfix
    date_en = reformat_date([date_ru], to_numeric=True, delimiter='.')[0]
    map_data = stored_data.query(f'vaccine == "{vaccines_dict[vac_type]}"')
    map_data = map_data[map_data['data_point'].str.contains(date_en)]
    map_data.rename(columns={'region': 'name'}, inplace=True)
    title_text = f'ЭВ в отношении предотвращения {title_cases[case]} COVID-19<br>({vac_type}, {age}, {date_ru})'
    map_figure = plot_choropleth_map(subjects, map_data, column, 'name', title_text)

    return map_figure


@app.callback(
    Output('interval_bar_chart', 'figure'),
    Input('store-int-data', 'data'),
    Input('subject', 'value'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value'),
    Input('month_year_int', 'value')
)
def update_interval_bar_chart(data, subject, vac_type, case, age, dates_list):
    chart_data = pd.DataFrame.from_dict(data)
    converted_dates = sorted(reformat_date(dates_list, to_numeric=True, delimiter='.'), key=lambda x: x.split("."))

    age_postfix = age_postfixes[age]
    column = 've_' + case + age_postfix
    ci_high_title = 'cih_' + case + age_postfix
    ci_low_title = 'cil_' + case + age_postfix
    title_text = f'ЭВ в отношении предотвращения {title_cases[case]} COVID-19<br>({vac_type}, {age}, {subject})'
    fig = plot_int_bar_chart(chart_data, converted_dates, column, [ci_low_title, ci_high_title], title_text)

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
    data = ve_6_age_gr.query(f'region == "{subject}" & vaccine == "{vaccines_dict[vac_type]}" &'
                             f'age_group == "{ages_dict[age]}"')
    fig = go.Figure()
    vac_intervals = {'21_45_days': '21-45 д.', '45_75_days': '45-75 д.',
                     '75_90_days': '75-90 д.', '90_105_days': '90-105 д.',
                     '105_165_days': '105-165 д.', '165_195_days': '165-195 д.'}
    converted_dates = sorted(reformat_date(dates, to_numeric=True, delimiter='.'), key=lambda x: x.split("."))
    for date in converted_dates:
        date = date.split("_")[0].rstrip('.B').split(".")
        y = data[data['data_point'].str.contains(".".join(date))]
        inversed_date = ".".join(date[::-1])
        x = [[inversed_date for _ in range(len(vac_intervals))], list(vac_intervals.values())]
        y.reset_index(drop=True, inplace=True)
        y = pd.concat([y.iloc[2:, :], y.loc[:1, :]])
        y = y[['ve_'+case, 'cil_'+case, 'cih_'+case]]
        cih = y['cih_'+case] - y['ve_'+case]
        cil = y['ve_'+case] - y['cil_'+case]
        title_text = f'ЭВ в отношении предотвращения {title_cases[case]} COVID-19<br>({vac_type}, ' \
                     f'{ages_dict[age]} лет, {subject})'
        bar_chart = go.Bar(x=x, y=y['ve_'+case], width=0.6, showlegend=False,
                           marker={'color': y['ve_'+case].fillna(0),
                                   'colorscale': [(0, "#c4c4c4"), (0.25, "#ff3333"),
                                                  (0.5, "#ffff66"), (1, "#81c662")],
                                   'opacity': 0.6, 'line': {'color': 'rgb(8,48,107)', 'width': 1}},
                           error_y=dict(type='data',
                                        symmetric=False,
                                        array=cih,
                                        arrayminus=cil,
                                        width=3,
                                        thickness=1.6),
                           hovertemplate="<br> ЭВ: %{y:.1%}<br> ДИ: "
                                         "+%{error_y.array:.1%} "
                                         "/ -%{error_y.arrayminus:.1%} "
                                         "<extra></extra>")
        fig.add_trace(bar_chart)
        fig.update_yaxes(tickformat='.0%')
        fig.update_layout(autosize=False, separators=',', template='plotly_white',
                          margin={'l': 30, 'b': 25, 't': 90, 'r': 20}, title={'text': title_text, 'x': 0.5, 'y': 0.95,
                                                                              'xanchor': 'center', 'yanchor': 'top',
                                                                              'font': {'size': 15}})
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
    if pie_chart_data.shape[0] == 0:
        labels = ['Данные отсутствуют']
        values = [1]
        show_text = 'none'
    else:
        labels = list(pie_chart_data['pango_lineage'].values[0].keys())
        values = list(pie_chart_data['pango_lineage'].values[0].values())
        show_text = 'inside'
    date_ru = reformat_date([date], delimiter='-')
    title_text = f'Соотношение циркулирующих штаммов COVID-19 ({subject}, {date_ru[0]})'
    fig = go.Figure(data=[go.Pie(labels=labels, values=values,
                                 hovertemplate="%{label}<br>%{percent}"
                                               "<extra></extra>")])
    fig.update_traces(textposition=show_text)
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide',
                      legend={'x': 0.85})
    fig.update_layout(autosize=True, separators=',',
                      template='seaborn', margin={'l': 0, 'b': 100, 't': 0, 'r': 0},
                      paper_bgcolor='white',
                      title={'text': title_text,  'x': 0.5, 'y': 0.05,
                             'xanchor': 'center', 'yanchor': 'bottom', 'font': {'size': 15}})

    return [fig, date_options]


if __name__ == '__main__':
    app.run_server(debug=True)
