from dash import Dash, html, dcc, Output, Input
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from utils import read_csv_files, extract_map_data, get_subjects, parse_files, get_graph_data


csv_folder_path = './input_csv_files'
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

""" APP """
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.layout = html.Div([
        html.Div([
            html.H1(children='Визуализация эффективности вакцинации'),
            html.Hr(),
            html.P('''* показатели ЭВ рассчитанны по данным выгрузок регистра заболевших COVID-19
                   и регистра вакцинированных на 15 число месяца, следующего за отчетным''',
                   style={}),
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
                            children=[dcc.Graph(id='graph',
                                                # figure=figure,
                                                config=dict(responsive=True),
                                                style={'margin': '20px 40px 10px 40px',
                                                       'verticalAlign': 'middle',
                                                       'height': '55vh',
                                                       'backgroundColor': 'white'})]),
                    dbc.Tab(label='Штаммы')
                ], style={'margin': '20px 40px 10px 40px'})
            ], className="shadow p-3 mb-5 bg-white rounded",
               style={'width': '80%'}),

        ], style={'display': 'flex', 'flex-direction': 'row',
                  'gap': '50px', 'margin': '40px 40px 0px 40px'}),

        html.Div([
            dcc.Graph(id='map',
                      # figure=map_figure,
                      className="shadow p-3 mb-5 bg-white rounded",
                      style={'width': '65%', 'height': '65vh'}),
            html.Div([dcc.Graph(id='hbar_data')],  # figure=total_ve_russia
                     className="shadow p-3 mb-5 bg-white rounded",
                     style={'width': '35%'})
        ], style={'display': 'flex', 'flex-direction': 'row', 'gap': '50px',
                  'margin': '0px 40px'})  # 'backgroundColor': 'white'

], style={'width': '100%',
              'margin': '0px',
              'height': '100%',
              'backgroundColor': '#eaeaf2'})


@app.callback(
    Output('graph', 'figure'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value')
)
def update_bar_v(vac_type, case, age):
    case_prefix = case
    age_prefix = '_18_59_R'
    if age == 'от 18 до 59 лет':
        age_prefix = '_18_59_R'
    elif age == 'от 60 лет и старше':
        age_prefix = '_60_R'
    else:
        age_prefix = '_total_R'

    column = case_prefix + '_ve' + age_prefix
    ci_high_title = case_prefix + '_cih' + age_prefix
    ci_low_title = case_prefix + '_cil' + age_prefix
    graph_data = bar_chart_data[bar_chart_data['vaccine'] == vac_type]
    data_y = graph_data[column]
    ci_high = graph_data[ci_high_title] - data_y
    ci_low = data_y - graph_data[ci_low_title]
    data_x = [i for i in range(data_y.shape[0])]
    tick_text = graph_data['date'].dt.strftime('%m.%Y')
    figure = go.Figure(data=[go.Bar(x=data_x,
                                    y=data_y,
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

    figure.update_layout(paper_bgcolor="white", template='none')
    figure.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                         marker_line_width=1.5, opacity=0.6)
    figure.update_layout(margin={'l': 50, 'b': 20, 't': 90, 'r': 20}, separators=',',
                         template='none',
                         xaxis={'tickmode': 'array', 'tickvals': data_x, 'ticktext': tick_text},
                         title={'text': 'Эффективность выбранной вакцины за определенный период',
                                'x': 0.5, 'y': 0.96, 'xanchor': 'center', 'yanchor': 'top'})
    return figure


@app.callback(
    Output('hbar_data', 'figure'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value'),
    Input('month_year', 'value')
)
def update_bar_h(case, age, date_ru):
    case_prefix = case
    age_prefix = '_18_59_R'
    if age == 'от 18 до 59 лет':
        age_prefix = '_18_59_R'
    elif age == 'от 60 лет и старше':
        age_prefix = '_60_R'
    else:
        age_prefix = '_total_R'
    column = case_prefix + '_ve' + age_prefix
    month, year, _ = date_ru.split(" ")
    date_en = f'{year}-{ru_en_month[month]}-15'
    data_x = bar_chart_data[bar_chart_data['date'] == date_en][column]
    data_y = bar_chart_data[bar_chart_data['date'] == date_en]['vaccine']
    figure = go.Figure(data=[go.Bar(x=data_x, y=data_y,
                                    orientation='h',
                                    marker={'color': data_x, 'colorscale': 'dense_r'},
                                    hovertemplate="<br> ЭВ: %{x:.1%}<extra></extra>")])
    figure.update_layout(template='none',
                                  xaxis_range=[data_x.min(), data_x.max()],
                                  autosize=True,
                                  margin={"r": 50, "t": 130, "l": 130, "b": 0})
    figure.update_layout(title={'text': 'Эффективность различных вакцин <br>за выбранный период',
                                         'y': 0.92, 'x': 0.5,
                                         'xanchor': 'center', 'yanchor': 'top'})
    return figure


@app.callback(
    Output('map', 'figure'),
    Input('vaccine_type', 'value'),
    Input('disease_severity', 'value'),
    Input('age_group', 'value'),
    Input('month_year', 'value'),
)
def update_map(vac_type, case, age, date):
    case_prefix = case
    age_prefix = '_18_59_R'

    if age == 'от 18 до 59':
        age_prefix = '_18_59_R'
    elif age == 'от 60 и старше':
        age_prefix = '_60_R'
    else:
        age_prefix = '_total_R'

    column = case_prefix + '_ve' + age_prefix
    map_data = data[vac_type][date].iloc[:-1, :]
    map_figure = go.Figure(go.Choroplethmapbox(
        geojson=subjects,
        locations=map_data['name'],
        featureidkey="properties.name",
        z=map_data[column],
        colorscale='dense_r',
        hovertemplate=' Субъект: %{location}<br> ЭВ: %{z:.1%}<extra></extra>',
    ))
    map_figure.update_traces(colorbar={'bgcolor': 'white',
                                       'orientation': 'v',
                                       'xanchor': 'center',
                                       'yanchor': 'middle',
                                       'tickmode': 'auto',
                                       'tickformat': ".0%",
                                       'ticks': 'outside',
                                       'tickfont': {'size': 15},
                                       'xpad': 20,
                                       'len': 0.8,
                                       'title': {'text': 'ЭB',
                                                 'font': {'size': 15}}},
                             hoverlabel={'font': {'size': 16},
                                         'namelength': -1},
                             selector=dict(type='choroplethmapbox'))
    map_figure.update_layout(mapbox_style='white-bg',  # "white-bg",
                             autosize=True,
                             paper_bgcolor='white',
                             plot_bgcolor='white',
                             mapbox=dict(center=dict(lat=70, lon=105), zoom=1.8))
    map_figure.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
    map_figure.update_geos(fitbounds="locations")
    map_figure.update_layout(title={'text': 'Эффективность вакцинации по субъектам РФ',
                                    'x': 0.5, 'y': 0.95, 'font_color': 'black',
                                    'xanchor': 'center', 'yanchor': 'top'})
    return map_figure


if __name__ == '__main__':
    app.run_server(debug=True)
