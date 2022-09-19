import dash_bootstrap_components as dbc
from dash import html, dcc

from utils import get_months

vaccines = ['Спутник V', 'Спутник Лайт', 'ЭпиВак', 'КовиВак', 'Все вакцины']
age_groups = ['от 18 до 59 лет', 'от 60 лет и старше', 'все']
covid_cases = [{'label': 'заразившиеся', 'value': 'zab'},
               {'label': 'госпитализированные', 'value': 'st'},
               {'label': 'с тяжелой формой', 'value': 'tyazh'},
               {'label': 'умершие', 'value': 'sm'}]

modeBarButtonsToRemove = ['autoScale2d', 'pan2d', 'zoom2d', 'select2d', 'lasso2d']
config = dict(displaylogo=False,  responsive=True,  modeBarButtonsToRemove=modeBarButtonsToRemove)
csv_folder_path = r'./data/input_csv_files'
month_list = list(get_months(csv_folder_path).keys())


def make_layout():
    layout = html.Div([
                html.Div([
                    html.H1(children='Визуализация эффективности вакцинации'),
                    html.Hr(),
                    html.P('''* показатели ЭВ рассчитаны по данным выгрузок регистра заболевших COVID-19
                              и регистра вакцинированных на 15-е число месяца, следующего за отчетным'''),
                ], className='header'),

                html.Div([
                    # Div container for Dropdown menu
                    html.Div([
                        html.H5('Фильтры', className='dropdown-filter-label'),
                        html.Hr(className='dropdown'),
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
                                       inputStyle={"margin-right": "15px"},
                                       className='dropdown'),
                        html.Label('Месяц и год', className='dropdown-label'),
                        dcc.Dropdown(options=month_list,
                                     value=month_list[0],
                                     id='month_year',
                                     clearable=False,
                                     className='dropdown')
                    ], className='dropdown-container shadow p-3 mb-5 bg-white rounded'),

                    # Div container for tabs with graphs
                    html.Div([
                        dbc.Tabs([
                            dbc.Tab(label='Общая ЭВ',
                                    children=[dcc.Graph(id='bar_chart_v',
                                                        config=config,
                                                        className='bar-chart-v')]),
                            dbc.Tab(label='Штаммы',
                                    children=[html.Div('Данные отсутствуют',
                                                       className='strains-graph')])
                        ], className='tabs')
                    ], className='tabs-container shadow p-3 mb-5 bg-white rounded'),
                ], className='dropdown-tabs-container'),

                html.Div([
                    html.Div([
                        dcc.Loading(id="loading",
                                    children=dcc.Graph(id='map',
                                                       config=config,
                                                       className='map'),
                                    type="circle")
                    ], className='map-container shadow p-3 mb-5 bg-white rounded'),
                    html.Div([
                        dcc.Graph(id='bar_chart_h',
                                  config=config)
                    ], className='bar-chart-h-container shadow p-3 mb-5 bg-white rounded')
                ], className='map-bar-chart-container'),

                dcc.Store(id='store-data', storage_type='session'),
                dcc.Store(id='store-chart-data', storage_type='session'),
                html.Div(id='test')

            ], className='app-div-container')

    return layout
