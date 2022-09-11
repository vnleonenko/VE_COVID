from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import os
import pandas as pd
from datetime import date
from utils import read_csv_files, extract_map_data, get_subjects


geojson_path = r'./map_data/admin_level_4_copy.geojson'
csv_folder_path = r'./input_csv_files'

data_df = pd.read_csv(r'./synthetic_data.csv',  delimiter=';', decimal=',', encoding='cp1251')
data_df['date'] = pd.to_datetime(data_df['date'], dayfirst=True, infer_datetime_format=True)

csv_files = read_csv_files(csv_folder_path)
months_map_data = list(csv_files.keys())

map_data_dict = {}
for csv_file, month in zip(os.listdir(csv_folder_path), months_map_data):
    data = extract_map_data(os.path.join(csv_folder_path, csv_file))
    map_data_dict.update({month: data})
subjects = get_subjects(geojson_path)

""" APP """
app = Dash(__name__)

dropdown_font = {'fontFamily': 'Century Gothic, monospace'}

app.layout = html.Div([
    html.Div([
        html.H1(children='Визуализация эффективности вакцинации', style={'padding': '0px 10px'}),
        # html.P(children='Описание', style={'padding': '5px 10px'}),
    ], style={'margin': '10px 40px 10px 40px',
              'backgroundColor': '#eff2f6',
              'height': '120px',
              'fontFamily': 'Century Gothic, monospace',
              'padding': '20px 0px 0px 20px'}),
    html.Div([
        # Div container for the graph and the range to show
        dcc.Graph(
            id='graph',
            config=dict(responsive=True),
            style={'margin': '20px 0px 10px 40px',
                   'height': '55vh', 'width': '70%',
                   'fontFamily': 'Century Gothic, monospace',
                   'backgroundColor': 'white'}),
        # Div container for options to select
        html.Div([
            html.Label(children='Выберите тип вакцины', style={'fontSize': '18px',
                                                               'fontFamily': 'Century Gothic, monospace',
                                                               }),
            dcc.Dropdown(['Спутник V', 'Спутник Лайт', 'ЭпиВакКоронa', 'КовиВак', 'Все'],
                         value='Спутник V',
                         placeholder="Выбрать...",
                         id='vaccine_type',
                         clearable=False,
                         style={'margin': '10px 10px 20px 0px',
                                'width': '100%',
                                'fontFamily': dropdown_font['fontFamily']}),
            html.Label(children='Выберите возрастную группу', style={'fontSize': '18px',
                                                                     'fontFamily': dropdown_font['fontFamily']}),
            dcc.Dropdown(['от 18 до 59 лет', 'от 60 лет и старше', 'все'],
                         value='от 18 до 59 лет',
                         placeholder="Выбрать...",
                         id='age_group',
                         clearable=False,
                         style={'margin': '10px 10px 20px 0px',
                                'width': '100%',
                                'fontFamily': dropdown_font['fontFamily']}),
            html.Label(children='Выберите показатель ЭВ', style={'fontSize': '18px',
                                                                       'fontFamily': dropdown_font['fontFamily']}),
            dcc.Dropdown(['заразившиеся', 'госпитализированные', 'с тяжелой формой', 'умершие'],
                         value='заразившиеся',
                         placeholder="Выбрать...",
                         id='disease_severity',
                         clearable=False,
                         style={'margin': '10px 10px 20px 0px',
                                'width': '100%',
                                'fontFamily': dropdown_font['fontFamily']})
        ], style={'margin': '20px 40px 0px 30px',
                  'backgroundColor': 'white',
                  'width': '30%', 'height': '50vh'}),
    ], style={'display': 'flex', 'flex-direction': 'row'}),
    html.Div([
        html.Label('Начало интервала:', style={'margin': '5px 10px 0px 30px',
                                               'fontFamily': 'Century Gothic, monospace'}),
        dcc.DatePickerSingle(
            id='start_range',
            min_date_allowed=date(2022, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date(2022, 7, 11),
            date=date(2022, 1, 1),
            display_format='D.M.Y'
        ),
        html.Label('Конeц интервала:', style={'margin': '5px 10px 0px 30px',
                                              'fontFamily': 'Century Gothic, monospace'}),
        dcc.DatePickerSingle(
            id='end_range',
            min_date_allowed=date(2020, 1, 1),
            max_date_allowed=date(2022, 7, 10),
            initial_visible_month=date(2022, 7, 11),
            date=date.today(),
            display_format='D.M.Y'
        )
    ], style={'margin': '20px 30px 0px 40px',
              'backgroundColor': 'white'}),

    html.Div([
        html.H1('Эффективность вакцинации по субъектам РФ',
                style={'margin': '60px 10px 0px 40px',
                       'fontFamily': 'Century Gothic, monospace'}),
        html.Div([
            html.Div([
                html.Label(children='Выберите тип вакцины', style={'fontSize': '18px',
                                                                   'fontFamily': 'Century Gothic, monospace',
                                                                   }),
                dcc.Dropdown(['Спутник V', 'Спутник Лайт', 'ЭпиВакКоронa', 'КовиВак'],
                             value='Спутник V',
                             placeholder="Выбрать...",
                             id='vaccine_type_map',
                             clearable=False,
                             style={'margin': '10px 10px 20px 0px',
                                    'width': '100%',
                                    'fontFamily': dropdown_font['fontFamily']}),
            ], style={'width': '20%'}),
            html.Div([
                html.Label(children='Выберите возрастную группу', style={'fontSize': '18px',
                                                                         'fontFamily': dropdown_font['fontFamily']}),
                dcc.Dropdown(['от 18 до 59 лет', 'от 60 лет и старше', 'все'],
                             value='от 18 до 59 лет',
                             placeholder="Выбрать...",
                             id='age_group_map',
                             clearable=False,
                             style={'margin': '10px 10px 20px 0px',
                                    'width': '100%',
                                    'fontFamily': dropdown_font['fontFamily']}),
            ], style={'width': '21%'}),
            html.Div([
                html.Label(children='Выберите показатель ЭВ', style={'fontSize': '18px',
                                                                     'fontFamily': dropdown_font['fontFamily']}),
                dcc.Dropdown(['заразившиеся', 'госпитализированные', 'с тяжелой формой', 'умершие'],
                             value='заразившиеся',
                             placeholder="Выбрать...",
                             id='disease_severity_map',
                             clearable=False,
                             style={'margin': '10px 10px 20px 0px',
                                    'width': '100%',
                                    'fontFamily': dropdown_font['fontFamily']})
            ], style={'width': '20%'}),
        ], style={'margin': '30px 10px 0px 40px',
                  'display': 'flex',
                  'flex-direction': 'row',
                  'flexWrap': 'wrap',
                  'gap': '50px'}),
        html.Div([
                html.Label('Выберите месяц и год *', style={'fontSize': '18px',
                                                            'fontFamily': dropdown_font['fontFamily']}),
                dcc.Dropdown(options=months_map_data,
                             value=months_map_data[0],
                             placeholder="Выбрать...",
                             id='date_map',
                             clearable=False,
                             style={'margin': '10px 10px 20px 0px',
                                    'width': '100%',
                                    'fontFamily': dropdown_font['fontFamily']})
            ], style={'width': '19.5%', 'margin': '20px 0px 30px 40px'}),
        html.P('''* показатели ЭВ, рассчитанные по данным выгрузок регистра заболевших COVID-19
                и регистра вакцинированных на 15 число месяца, следующего за отчетным
               ''', style={'margin': '30px 0px 30px 40px',
                           'fontFamily': dropdown_font['fontFamily']}),
        html.Div(
            html.Div(id='ve_russia',
                     style={'margin': '20px 40px 30px 40px',
                            'width': '45%',
                            'height': '50px',
                            'padding': '20px 0px 0px 20px',
                            'backgroundColor': '#eff2f6',
                            'fontSize': '25px',
                            'fontFamily': dropdown_font['fontFamily']}),
            style={'display': 'flex',
                   'flex-direction': 'row',
                   'justifyContent': 'flex-end'}
        ),
        html.Div([
            dcc.Graph(id='map')
        ])
    ])

])


@app.callback(
    Output('graph', "figure"),
    Input('disease_severity', 'value'),
    Input('age_group', 'value')
)
def update_graph(case, age):
    case_prefix = 'zab'
    age_prefix = '_18_59_R'
    color = '#5c85d6'

    if age == 'от 18 до 59':
        age_prefix = '_18_59_R'
    elif age == 'от 60 и старше':
        age_prefix = '_60_R'
    else:
        age_prefix = '_total_R'

    if case == 'заболевшие':
        case_prefix = 'zab'
        color = '#5c85d6'

    elif case == 'госпитализированные':
        case_prefix = 'st'
        color = '#ff8080'

    elif case == 'с тяжелой формой':
        case_prefix = 'tyazh'
        color = '#6fdc6f'

    elif case == 'умершие':
        case_prefix = 'sm'
        color = '#669999'

    column = case_prefix + '_ve' + age_prefix
    ci_high_title = case_prefix + '_cih' + age_prefix
    ci_low_title = case_prefix + '_cil' + age_prefix
    data_y = data_df[column]
    ci_high = data_df[ci_high_title]
    ci_low = data_df[ci_low_title]
    # print(data_df.shape[0], [0.5 for _ in range(data_df.shape[0])])
    data_x = [i for i in range(data_y.shape[0])]
    figure = go.Figure(data=[go.Bar(x=data_x,
                                    y=data_y,
                                    width=0.6,
                                    error_y=dict(
                                        type='data',
                                        symmetric=False,
                                        array=ci_high,
                                        arrayminus=ci_low,
                                        width=5,
                                        thickness=3),
                                    marker_color=color)])
    figure.update_layout(margin={'l': 20, 'b': 30, 't': 0, 'r': 20})
    figure.update_layout(
        xaxis={'tickmode': 'array', 'tickvals': data_x, 'ticktext': data_df['date'].dt.strftime('%m.%Y')})
    figure.update_yaxes(range=[0, data_y.max() + 0.5 * data_y.max() + ci_high.max()])
    figure.update_layout(separators=',')

    return figure


@app.callback(
    [Output('map', 'figure'),
     Output('ve_russia', 'children')],
    Input('disease_severity_map', 'value'),
    Input('age_group_map', 'value'),
    Input('date_map', 'value'),
)
def update_map(case, age, date):
    case_prefix = 'zab'
    age_prefix = '_18_59_R'

    if age == 'от 18 до 59':
        age_prefix = '_18_59_R'
    elif age == 'от 60 и старше':
        age_prefix = '_60_R'
    else:
        age_prefix = '_total_R'

    if case == 'заболевшие':
        case_prefix = 'zab'

    elif case == 'госпитализированные':
        case_prefix = 'st'

    elif case == 'с тяжелой формой':
        case_prefix = 'tyazh'

    elif case == 'умершие':
        case_prefix = 'sm'

    column_name = case_prefix + '_ve' + age_prefix
    # csv_path = os.path.join(csv_folder_path, csv_files[date])
    # data = extract_map_data(csv_path)

    map_data = map_data_dict[date]
    ve_russia = round(map_data[map_data['name'] == 'РФ'][column_name].item() * 100, 1)
    map_data = map_data.iloc[:-1, :]
    fig = go.Figure(go.Choroplethmapbox(
        geojson=subjects,
        locations=map_data['name'],
        featureidkey="properties.name",
        z=map_data[column_name],
        colorscale='YlGnBu',
        hovertemplate='<b> Субъект: %{location}</b><br><b> ЭВ: %{z:.1%}</b><extra></extra>'
    ))
    fig.update_traces(colorbar={'bgcolor': 'white',
                                'tickmode': 'auto',
                                'tickformat': ".0%",
                                'ticks': 'outside',
                                'tickfont': {'family': dropdown_font['fontFamily'],
                                             'size': 20},
                                'xpad': 50,
                                'len': 0.8,
                                'title': {'text': 'Эффективность<br>вакцинации',
                                          'font': {'family': dropdown_font['fontFamily'],
                                                   'size': 20}
                                          },
                                },
                      hoverlabel={'font': {'size': 18,
                                           'family': dropdown_font['fontFamily']},
                                  'namelength': -1
                      },
                      selector=dict(type='choroplethmapbox')
                      ),
    fig.update_layout(mapbox_style="white-bg",
                      height=1000,
                      autosize=True,
                      margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      paper_bgcolor='white',
                      plot_bgcolor='white',
                      mapbox=dict(center=dict(lat=70, lon=105), zoom=2.5),

                      )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_geos(fitbounds="locations")
    ve_russia_output = f'Показатель ЭВ по Российской Федерации : {str(ve_russia).replace(".", ",")} %'
    return [fig, ve_russia_output]


if __name__ == '__main__':
    app.run_server(debug=True)
