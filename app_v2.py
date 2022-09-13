import pandas as pd
from dash import Dash, html, dcc, Output, Input, State, ClientsideFunction
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from utils import get_subjects, parse_files, get_graph_data
from copy import deepcopy

csv_folder_path = 'input_csv_files'
data = parse_files(csv_folder_path)
bar_chart_data = get_graph_data(data)

geojson_path = r"./map_data/admin_level_4_copy.geojson"
subjects = get_subjects(geojson_path)

months_map_data = list(data['Все вакцины'].keys())
ru_en_month = {'январь': '01', 'февраль': '02', 'март': '03',
               'апрель': '04', 'май': '05', 'июнь': '06',
               'июль': '07', 'август': '08', 'сентябрь': '09',
               'октябрь': '10', 'ноябрь': '11', 'декабрь': '12'}

dd_margin_left = '20px'
config = {'displayModeBar': False}

""" APP """
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server_v2 = app.server
app.layout = html.Div([
        html.Div([
            html.H1(children='Визуализация эффективности вакцинации'),
            html.Hr(),
            html.P('''* показатели ЭВ рассчитаны по данным выгрузок регистра заболевших COVID-19
                   и регистра вакцинированных на 15-е число месяца, следующего за отчетным'''),
        ], style={'margin': '10px 40px 10px 40px',
                  'padding': '20px 0px 0px 0px'}),

        html.Div([
            # Div container for Dropdown menu
            html.Div([
                html.H5('Фильтры', style={'marginLeft': dd_margin_left, 'marginTop': '10px'}),
                html.Hr(style={'margin': '10px 10px 20px 10px',
                               'width': '80%'}),
                html.Label(children='Тип вакцины', style={'fontSize': '18px',
                                                          'marginLeft': dd_margin_left}),
                dcc.Dropdown(['Спутник V', 'Спутник Лайт', 'ЭпиВак', 'КовиВак', 'Все вакцины'],
                             value='Спутник V',
                             id='vaccine_type',
                             clearable=False,
                             style={'margin': '10px 10px 20px 10px',
                                    'width': '80%'}),
                html.Label(children='Возрастная группа', style={'fontSize': '18px',
                                                                'marginLeft': dd_margin_left}),
                dcc.Dropdown(['от 18 до 59 лет', 'от 60 лет и старше', 'все'],
                             value='от 18 до 59 лет',
                             id='age_group',
                             clearable=False,
                             style={'margin': '10px 10px 20px 10px',
                                    'width': '80%'}),
                html.Label(children='Показатель ЭВ', style={'fontSize': '18px',
                                                            'marginLeft': dd_margin_left}),
                dcc.RadioItems([{'label': 'заразившиеся', 'value': 'zab'},
                                {'label': 'госпитализированные', 'value': 'st'},
                                {'label': 'с тяжелой формой', 'value': 'tyazh'},
                                {'label': 'умершие', 'value': 'sm'}],
                               value='zab',
                               id='disease_severity',
                               labelStyle={'display': 'block'},
                               inputStyle={"margin-right": "15px"},
                               style={'margin': '10px 10px 20px 20px',
                                      'width': '80%'}),
                html.Label('Месяц и год', style={'fontSize': '18px',
                                                 'marginLeft': dd_margin_left}),
                dcc.Dropdown(options=months_map_data,
                             value=months_map_data[0],
                             id='month_year',
                             clearable=False,
                             style={'margin': '10px 10px 20px 10px',
                                    'width': '80%'})
            ], className="shadow p-3 mb-5 bg-white rounded",
               style={'width': '35%',
                      'backgroundColor': 'white',
                      'border-radius': '10px'}),

            # Div container for tabs with graphs
            html.Div([
                dbc.Tabs([
                    dbc.Tab(label='Общая ЭВ',
                            children=[dcc.Graph(id='bar_chart_v',
                                                # figure=figure,
                                                config=dict(displaylogo=False,
                                                            responsive=True,
                                                            modeBarButtonsToRemove=['autoScale2d', 'pan2d', 'zoom2d',
                                                                                    'select2d', 'lasso2d'],
                                                            ),
                                                style={'margin': '20px 40px 10px 40px',
                                                       'verticalAlign': 'middle',
                                                       'height': '55vh',
                                                       'backgroundColor': 'white'})]),
                    dbc.Tab(label='Штаммы',
                            children=[
                                html.Div('Данные отсутствуют',
                                         style={'margin': '20px 40px 10px 40px',
                                                'verticalAlign': 'middle',
                                                'height': '55vh',
                                                'backgroundColor': 'white'})
                            ])
                ], style={'margin': '20px 40px 10px 40px'})
            ], className="shadow p-3 mb-5 bg-white rounded",
               style={'width': '80%'}),

        ], style={'display': 'flex', 'flex-direction': 'row',
                  'gap': '50px', 'margin': '40px 40px 0px 40px'}),

        html.Div([
            html.Div([
                dcc.Loading(id="loading",
                            children=dcc.Graph(id='map',
                                               # className="shadow p-3 mb-5 bg-white rounded",
                                               config=dict(displaylogo=False,
                                                           modeBarButtonsToRemove=['autoScale2d', 'pan2d', 'zoom2d',
                                                                                   'select2d', 'lasso2d'],
                                                           responsive=True),
                                               style={'height': '65vh'}),
                            type="circle")
            ], className="shadow p-3 mb-5 bg-white rounded",
               style={'width': '65%', 'height': '70vh', 'backgroundColor': 'white'}),
            html.Div([
                dcc.Graph(id='bar_chart_h',
                          config=dict(displaylogo=False,
                                      modeBarButtonsToRemove=['autoScale2d', 'pan2d', 'zoom2d', 'select2d', 'lasso2d'],
                                      responsive=True))
            ], className="shadow p-3 mb-5 bg-white rounded",
               style={'width': '35%'})
        ], style={'display': 'flex', 'flex-direction': 'row', 'gap': '50px',
                  'margin': '0px 40px'}),

        dcc.Store(id='store-data', storage_type='session'),
        dcc.Store(id='store-chart-data', storage_type='session'),


], style={'width': '100%',
          'height': '100%',
          'backgroundColor': '#eaeaf2'})


@app.callback(
    Output('store-data', 'data'),
    Output('store-chart-data', 'data'),
    Input('age_group', 'value'),
)
def update_store(age):
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
    State('store-chart-data', 'data'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value'),
    Input('month_year', 'value')
)
def update_bar_chart(stored_data, vac_type, case, age, date_ru):
    stored_data = pd.DataFrame(stored_data)
    #print(stored_data['date'].dtype)
    stored_data['date'] = pd.to_datetime(stored_data['date'], dayfirst=True, infer_datetime_format=True)
    #print(stored_data.head())
    #print(stored_data['date'][0])
    case_prefix = case
    age_prefix = '_18_59_R'
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
    graph_data_v = stored_data[stored_data['vaccine'] == vac_type]
    data_y_v = graph_data_v[column]
    ci_high = graph_data_v[ci_high_title] - data_y_v
    ci_low = data_y_v - graph_data_v[ci_low_title]
    data_x_v = [i for i in range(data_y_v.shape[0])]
    #graph_data_v = pd.to_datetime(graph_data_v['date'], dayfirst=True, infer_datetime_format=True)
    tick_text = graph_data_v['date'].dt.strftime('%m.%Y')
    title_text = f'ЭВ в отношении предотвращения {title_case} COVID-19 <br>({vac_type}, {age})'
    bar_chart_v = go.Figure(data=[go.Bar(x=data_x_v,
                                         y=data_y_v,
                                         width=0.5,
                                         error_y=dict(
                                                     type='data',
                                                     symmetric=False,
                                                     array=ci_high,
                                                     arrayminus=ci_low,
                                                     width=4,
                                                     thickness=2),
                                         hovertemplate="<br> ЭВ: %{y:.1%}<br> ДИ+ %{error_y.array:.1%}"
                                                       "<br> ДИ- %{error_y.arrayminus:.1%} <extra></extra>")])

    bar_chart_v.update_layout(paper_bgcolor="white", template='none')
    bar_chart_v.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                              marker_line_width=1.5, opacity=0.6)
    bar_chart_v.update_layout(margin={'l': 50, 'b': 20, 't': 110, 'r': 20},
                              template='none',
                              xaxis={'tickmode': 'array', 'tickvals': data_x_v, 'ticktext': tick_text},
                              yaxis_tickformat='.0%',
                              separators=',',
                              title={'text': title_text, 'x': 0.5, 'y': 0.9, 'xanchor': 'center', 'yanchor': 'top'})

    month, year, _ = date_ru.split(" ")
    date_en = f'{year}-{ru_en_month[month]}-15'
    data_x_h = stored_data[stored_data['date'] == date_en][column]
    data_y_h = stored_data[stored_data['date'] == date_en]['vaccine']
    title_text = f'ЭВ в отношении предотвращения {title_case} COVID-19<br>({age}, {date_ru})'
    bar_chart_h = go.Figure(data=[go.Bar(x=data_x_h, y=data_y_h,
                                         orientation='h',
                                         marker={'color': data_x_h,
                                                 'colorscale': [(0, "#4d56b3"), (1, "#9ecae1")],
                                                 'opacity': 0.8,
                                                 'line': {'color': 'rgb(8,48,107)',
                                                          'width': 1.5}},

                                         hovertemplate="<br> ЭВ: %{x:.1%}<extra></extra>")])
    bar_chart_h.update_layout(template='plotly_white',
                              xaxis={'showticklabels': True},
                              xaxis_tickformat='.0%',
                              autosize=False,
                              margin={"r": 50, "t": 130, "l": 130, "b": 0})
    bar_chart_h.update_xaxes(zeroline=True, zerolinewidth=1, zerolinecolor='black')
    bar_chart_h.update_yaxes(zeroline=True, zerolinewidth=1, zerolinecolor='black')
    bar_chart_h.update_layout(title={'text': title_text, 'font_color': 'black',
                                     'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                              title_font_size=14)

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
    age_prefix = '_18_59_R'
    title_case = ''

    if age == 'от 18 до 59':
        age_prefix = '_18_59_R'
    elif age == 'от 60 и старше':
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
    map_figure = go.Figure(go.Choroplethmapbox(
        geojson=subjects,
        locations=map_data['name'],
        featureidkey="properties.name",
        z=map_data[column],
        colorscale=[(0, "#4d56b3"), (0.5, "#ffffff"), (1, "#81c662 ")],
        hovertemplate=' Субъект: %{location}<br> ЭВ: %{z:.1%}<extra></extra>',
    ))
    map_figure.update_traces(colorbar={'bgcolor': 'white',
                                       'orientation': 'v',
                                       'xanchor': 'center',
                                       'yanchor': 'middle',
                                       'tickmode': 'auto',
                                       'tickformat': ".0%",
                                       'ticks': 'outside',
                                       'tickfont': {'size': 14},
                                       'xpad': 20,
                                       'len': 0.8,
                                       'title': {'text': 'ЭB',
                                                 'font': {'size': 15}}},
                             hoverlabel={'font': {'size': 15},
                                         'namelength': -1},
                             selector=dict(type='choroplethmapbox'))
    map_figure.update_layout(mapbox_style='white-bg',  # "white-bg",
                             autosize=True,
                             paper_bgcolor='white',
                             plot_bgcolor='white',
                             mapbox=dict(center=dict(lat=70, lon=105), zoom=1.7))
    map_figure.update_layout(margin={"r": 0, "t": 80, "l": 0, "b": 0})
    map_figure.update_geos(fitbounds="locations")
    map_figure.update_layout(title={'text': title_text, 'font_color': 'black',
                                    'x': 0.5, 'y': 0.93, 'xanchor': 'center', 'yanchor': 'top'},
                             title_font_size=14)
    return map_figure


if __name__ == '__main__':
    app.run_server(debug=True)
