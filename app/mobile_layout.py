import dash_bootstrap_components as dbc
from dash import html, dcc

import interval_utils as iu


vaccines = ['Спутник V', 'Спутник Лайт', 'ЭпиВак', 'КовиВак', 'Все вакцины']
age_groups = ['от 18 до 59 лет', 'от 60 лет и старше', 'все']
covid_cases = [{'label': 'заразившиеся', 'value': 'zab'},
               {'label': 'с тяжелой формой', 'value': 'tyazh'},
               {'label': 'госпитализированные', 'value': 'st'},
               {'label': 'умершие', 'value': 'sm'}]

modeBarButtonsToRemove = ['autoScale2d', 'pan2d', 'zoom2d', 'select2d', 'lasso2d']
config = dict(displaylogo=False,  responsive=True,  modeBarButtonsToRemove=modeBarButtonsToRemove)

int_data_folder_path = './data/input_csv_files/interval'
dates_list = iu.get_months(int_data_folder_path)
subjects = {'РФ': 'Российская Федерация',
            'г. Санкт-Петербург': 'г. Санкт-Петербург',
            'Московская область': 'Московская область'}


def make_mobile_layout(month_list):
    layout = html.Div([
                dbc.Row(
                    dbc.Col(
                        html.Div([
                            html.H1(children='Визуализация эффективности вакцинации'),
                            html.Hr(),
                            html.P('''* показатели ЭВ рассчитаны по данным выгрузок регистра заболевших COVID-19
                                      и регистра вакцинированных на 15-е число месяца, следующего за отчетным'''),
                        ], className='header'), width={'size': 10, 'offset': 1},
                    )
                ),

                dbc.Row([
                    #  Div container for Dropdown menu
                    dbc.Col([
                        html.Div([
                            html.H5('Фильтры', className='dropdown-filter-label'),
                            html.Hr(className='dropdown'),
                            html.Label(children='Субъект', className='dropdown-label'),
                            dcc.Dropdown(list(subjects.values()),
                                         value='Российская Федерация',
                                         id='subject',
                                         clearable=False,
                                         className='dropdown'),
                            html.Label(children='Тип вакцины', className='dropdown-label'),
                            dcc.Dropdown(vaccines,
                                         value='Спутник V',
                                         id='vaccine_type',
                                         clearable=False,
                                         className='dropdown'),
                            html.Label(children='Возрастная группа', className='dropdown-label'),
                            dcc.Dropdown(age_groups,
                                         value='от 18 до 59 лет',
                                         id='age_group',
                                         clearable=False,
                                         className='dropdown'),
                            html.Label(children='Показатель ЭВ', className='dropdown-label'),
                            dcc.RadioItems(covid_cases,
                                           value='zab',
                                           id='disease_severity',
                                           labelStyle={'display': 'block'},
                                           inputStyle={"margin-right": "5px",
                                                       "margin-left": "15px"},
                                           inline=True,
                                           className='dropdown'),
                            html.Label('Месяц и год', className='dropdown-label'),
                            dcc.Dropdown(options=month_list,
                                         value=month_list[0],
                                         id='month_year',
                                         clearable=False,
                                         className='dropdown'),
                            html.Label('Месяц и год для интервальной ЭВ', className='dropdown-label'),
                            dcc.Dropdown(options=dates_list,
                                         value=dates_list[:3],
                                         id='month_year_int',
                                         multi=True,
                                         clearable=False,
                                         className='dropdown'),
                            dbc.Checklist(
                                options=[
                                    {"label": "Изменять карту", "value": 1},
                                ],
                                value=[],
                                id='dropdown',
                                inline=True,
                                className='dropdown'
                            ),
                        ], className='dropdown-container shadow p-3 mb-5 bg-white rounded'),
                    ],  xs=10, sm=8, md=10, lg=3),

                    # Div container for tabs with graphs
                    dbc.Col([
                        html.Div([
                            dbc.Tabs([
                                dbc.Tab(label='Общая ЭВ',
                                        children=[dcc.Graph(id='bar_chart_v',
                                                            config=config,
                                                            className='bar-chart-v')]),
                                dbc.Tab(label='Интервальная ЭВ',
                                        children=[dcc.Graph(id='interval_bar_chart',
                                                            config=config,
                                                            className='int-bar-chart')]),
                                dbc.Tab(label='Штаммы',
                                        children=[html.Div('Данные отсутствуют',
                                                           className='strains-graph')])
                            ], className='tabs')
                        ], className='tabs-container shadow p-3 mb-5 bg-white rounded'),
                    ], xs=10, sm=8, md=10, lg=7),
                ], justify="center"),
                dbc.Row([
                    dbc.Col(
                            html.Div([
                                dbc.Tabs([
                                    dbc.Tab(label='Общая ЭВ',
                                            children=
                                            dcc.Loading(
                                                dcc.Graph(id='map',
                                                          config=config,
                                                          className='map'),
                                            type="circle"))
                                ], className='tabs')
                            ], className='tabs-container shadow p-3 mb-5 bg-white rounded'),

                        xs=10, sm=8, md=10, lg=7),
                    dbc.Col(
                        dcc.Graph(id='bar_chart_h',
                                  config=config,
                                  className='bar-chart-h shadow p-3 mb-5 bg-white rounded'),
                        xs=10, sm=8, md=10, lg=3),
                ], justify="center"),
                dcc.Store(id='store-data', storage_type='session'),
                dcc.Store(id='store-chart-data', storage_type='session'),
                # dcc.Store(id='interval-data', storage_type='session')
            ], className='app-div-container')

    return layout