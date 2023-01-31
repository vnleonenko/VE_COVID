import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html, dcc

vaccines = [{'label': 'Спутник V', 'value': 'SputnikV'},
            {'label': 'Спутник Лайт', 'value': 'SputnikLite'},
            {'label': 'ЭпиВак', 'value': 'EpiVacCorona'},
            {'label': 'КовиВак', 'value': 'CoviVac'},
            {'label': 'Все вакцины', 'value': 'AllVaccines'}]

age_groups = [{'label': 'от 18 до 59 лет', 'value': '18-59'},
              {'label': 'от 60 лет и старше', 'value': '60+'},
              {'label': 'от 18 лет и старше', 'value': '18+'}]

covid_cases = [{'label': 'заболевшие', 'value': 'zab'},
               {'label': 'госпитализированные', 'value': 'hosp'},
               {'label': 'с тяжелой формой', 'value': 'severe'},
               {'label': 'умершие', 'value': 'death'}]

mode_bar_buttons_to_remove = ['autoScale2d', 'pan2d', 'zoom2d', 'select2d', 'lasso2d']
config = dict(displaylogo=False, responsive=True, modeBarButtonsToRemove=mode_bar_buttons_to_remove)

subjects = [{'label': 'Российская Федерация', 'value': 'РФ', },
            {'label': 'г. Санкт-Петербург', 'value': 'г. Санкт-Петербург', },
            {'label': 'Московская область', 'value': 'Московская область', }]


def make_mobile_layout(months, initial_values, login):
    subject_dropdown = dcc.Dropdown(subjects, value=initial_values['subject_value'],
                                    id='subject', clearable=False, className='dropdown')
    vaccine_dropdown = dcc.Dropdown(vaccines, value=initial_values['vaccine_value'],
                                    id='vaccine_type', clearable=False, className='dropdown')
    age_groups_dropdown = dcc.Dropdown(age_groups, value=initial_values['age_value'],
                                       id='age_group', clearable=False, className='dropdown')
    severity_dropdown = dcc.RadioItems(covid_cases, value=initial_values['case_value'],
                   id='disease_severity', labelStyle={'display': 'block'},
                   inputStyle={"marginRight": "5px",
                               "marginLeft": "15px"},
                   inline=False, className='dropdown')
    months_year_dropdown = dcc.Dropdown(id='month_year', options=months, value=months[0],
                                        clearable=False, className='dropdown')
    map_checklist = dcc.Checklist(options=[{'label': 'Изменять карту', 'value': True}],
                                  value=[True], id='map-checklist', className='dropdown',
                                  inputStyle={"marginRight": 15, "marginTop": 10})
    months_year_multiselect = dmc.MultiSelect(description="Выберите до 4х различных месяцев",
                                              value=months[:2], data=months, maxSelectedValues=4,
                                              dropdownPosition='top', zIndex=100, id='month_year_int',
                                              style={'height': '7%', 'margin': '10px 30px 20px 20px',
                                                     'fontSize': '20vi', 'fontFamily': 'Helvetica'})
    filters = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H5('Фильтры', className='dropdown-filter-label'),
                        html.Hr(className='dropdown'),
                        html.Label(children='Субъект', className='dropdown-label'),
                        subject_dropdown,
                        html.Label(children='Тип вакцины', className='dropdown-label'),
                        vaccine_dropdown,
                        html.Label(children='Возрастная группа', className='dropdown-label'),
                        age_groups_dropdown,
                        html.Label(children='Показатель ЭВ', className='dropdown-label'),
                        severity_dropdown,
                        html.Label('Месяц и год', className='dropdown-label'),
                        months_year_dropdown,
                        map_checklist,
                        html.Label('Месяц и год для интервальной ЭВ ', className='dropdown-label'),
                        months_year_multiselect
                    ])
                ])
            ], style={"overflow": "scroll"},
               className='dropdown-container shadow p-3 mb-5 bg-white rounded')

    tabs = dbc.Tabs([
                dbc.Tab(label='Общая ЭВ',
                        children=[
                            dcc.Graph(id='bar_chart_v',
                                      config=config,
                                      className='bar-chart-v')
                        ]),
                dbc.Tab(label='Интервальная ЭВ1',
                        children=[
                            dcc.Graph(id='interval_bar_chart',
                                      config=config,
                                      className='int-bar-chart')
                        ]),
                dbc.Tab(label='Интервальная ЭВ2',
                        children=[
                            dcc.Graph(id='interval_bar_chart2',
                                      config=config,
                                      className='int-bar-chart2'),
                            html.Div('Выберите возрастную группу',
                                     style={'marginLeft': 20,
                                            'marginBottom': 10}),
                            dcc.Slider(0, 6, 1, value=0,
                                       marks={0: '20-29', 1: '30-39',
                                              2: '40-49', 3: '50-59',
                                              4: '60-69', 5: '70-79',
                                              6: '80+'},
                                       id='age_slider')
                        ]),
                dbc.Tab(label='Общая ЭВ и штаммы',
                        children=[
                            dcc.Graph(id='strains_ve_graph',
                                      config=config,
                                      className='strains-graph')]
                        ),
            ], className='tabs')

    if login in ['test', 'full_access']:
        tabs_cor = []
        for tab in tabs.children:
            if tab.label != 'Интервальная ЭВ2':
                tabs_cor.append(tab)
        tabs.children = tabs_cor
    elif login == 'internal':
        pass
    else:
        tabs = dbc.Tabs([])

    map_graph = html.Div([dcc.Loading(
                          dcc.Graph(id='map',
                                    config=config,
                                    className='map'),
                          type="circle")
                ], className='map-container shadow p-3 mb-5 bg-white rounded')
    horiz_bar_chart = dcc.Graph(id='bar_chart_h', config=config,
                                className='bar-chart-h shadow p-3 mb-5 bg-white rounded')
    layout = dbc.Container([
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1(children='Визуализация эффективности вакцинации'),
                        html.Hr(),
                        html.P('''* показатели ЭВ рассчитаны по данным выгрузок регистра заболевших COVID-19
                                          и регистра вакцинированных на 15-е число месяца, следующего за отчетным'''),
                    ], className='header'),
                    dbc.Row([
                        # col1 dropdowns
                        dbc.Col([
                            filters
                        ], xs=12, md=12, lg=4, xl=4),
                        # col2 tabs
                        dbc.Col([
                            html.Div([
                                dbc.Row([
                                    dbc.Col([
                                       tabs])
                                ])
                            ], style={"overflow": "scroll"},
                               className='dropdown-container shadow p-3 mb-5 bg-white rounded')
                        ], xs=12, md=12, lg=8, xl=8)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            map_graph
                        ], xs=12, md=12, lg=8, xl=8),
                        dbc.Col([
                            horiz_bar_chart
                        ], xs=12, md=12, lg=4, xl=4)
                    ])
                ], xs=11, lg=11)
            ], justify='evenly'),
        ], style={'marginLeft': '0px', 'marginRight': '0px'}, className='app-div-container')
    ], fluid=True, className='container-fluid')

    return layout
