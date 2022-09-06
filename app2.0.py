from dash import Dash, html, dcc
import plotly.graph_objects as go

from VE_COVID.utils import read_csv_files, extract_map_data, get_subjects, parse_csv_files

dropdown_font = {'fontFamily': 'Century Gothic, monospace'}
csv_folder_path = r'/VE_visualization/input_csv_files'
csv_files = read_csv_files(csv_folder_path)
months_map_data = list(csv_files.keys())

data_dict = parse_csv_files(csv_folder_path)
data_x = [i for i in range(data_dict['Все'].shape[0])]
data_y = data_dict['Все']['zab_ve_18_59_R']
ci_high = data_dict['Все']['zab_cih_18_59_R']
ci_low = data_dict['Все']['zab_cil_18_59_R']

""" VE GRAPH """
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
                                )])

'''
# Add range slider
figure.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="1m",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6m",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="YTD",
                     step="year",
                     stepmode="todate"),
                dict(count=1,
                     label="1y",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)
'''

figure.update_layout(margin={'l': 20, 'b': 30, 't': 0, 'r': 20}, separators=',',
                     template='seaborn',
                     xaxis={'tickmode': 'array', 'tickvals': data_x,
                            'ticktext': data_dict['Все']['date'].dt.strftime('%m.%Y')})
figure.update_yaxes(range=[0, data_y.max() + 0.5 * data_y.max() + ci_high.max()])

""" TOTAL VE GRAPH """
x = [31.6, 33, -13, -17, 38]
total_ve_russia = go.Figure(data=[go.Bar(x=x, y=['Все вакцины', 'Спутник V', 'ЭпиВак', 'КовиВак', 'Спутник Лайт'],
                                         orientation='h',
                                         marker={'color': x, 'colorscale': 'RdYlBu'})])
total_ve_russia.update_layout(template='none', xaxis_range=[-20, 40],  # #EAEAF2ff - seaborn bg color
                              autosize=False, width=500, height=500)
total_ve_russia.update_yaxes(automargin=True)

""" MAP """
geojson_path = r"/VE_visualization/map_data/admin_level_4_copy.geojson"
subjects = get_subjects(geojson_path)
csv_path = 'input_csv_files/2021.11_01-07-2022_0.csv'
data = extract_map_data(csv_path)
map_data = data.iloc[:-1, :]
column_name = 'zab_ve_18_59_R'
ve_russia = round(data.loc[data.shape[0] - 1, column_name] * 100, 1)
map_figure = go.Figure(go.Choroplethmapbox(
    geojson=subjects,
    locations=map_data['name'],
    featureidkey="properties.name",
    z=map_data[column_name],
    colorscale='RdYlBu',
    hovertemplate='<b> Субъект: %{location}</b><br><b> ЭВ: %{z:.1%}</b><extra></extra>',
))
map_figure.update_traces(colorbar={'bgcolor': 'white',
                                   'orientation': 'v',
                                   'xanchor': 'center',
                                   #'y': 0,
                                   'yanchor': 'middle',
                                   'tickmode': 'auto',
                                   'tickformat': ".0%",
                                   'ticks': 'outside',
                                   'tickfont': {'family': dropdown_font['fontFamily'],
                                                'size': 15},
                                   'xpad': 20,
                                   'len': 0.6,
                                   'title': {'text': 'ЭB',
                                             'font': {'family': dropdown_font['fontFamily'],
                                                      'size': 15}}},
                         hoverlabel={'font': {'size': 16,
                                              'family': dropdown_font['fontFamily']},
                                     'namelength': -1},
                         selector=dict(type='choroplethmapbox'))
map_figure.update_geos(fitbounds="locations")
map_figure.update_layout(mapbox_style='white-bg',  # "white-bg",
                         autosize=True,
                         #paper_bgcolor='white',
                         #plot_bgcolor='white',
                         mapbox=dict(center=dict(lat=70, lon=105), zoom=1.8))
map_figure.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

""" APP """
app = Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1(children='Визуализация эффективности вакцинации'),
            html.Hr(),
            html.P('''* показатели ЭВ рассчитанны по данным выгрузок регистра заболевших COVID-19
                   и регистра вакцинированных на 15 число месяца, следующего за отчетным''',
                   style={
                       'fontFamily': dropdown_font['fontFamily']}),
        ], style={'margin': '10px 40px 10px 40px',
                  # 'backgroundColor': '#eff2f6',
                  'fontFamily': 'Century Gothic, monospace',
                  'padding': '20px 0px 0px 0px'}),

        html.Div([
            # Div container for Dropdown menu
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
                                    'fontFamily': dropdown_font['fontFamily']}),
                html.Label('Выберите месяц и год', style={'fontSize': '18px',
                                                          'fontFamily': dropdown_font['fontFamily']}),
                dcc.Dropdown(options=months_map_data,
                             value=months_map_data[0],
                             placeholder="Выбрать...",
                             id='date_map',
                             clearable=False,
                             style={'margin': '10px 10px 20px 0px',
                                    'width': '100%',
                                    'fontFamily': dropdown_font['fontFamily']})
            ], style={'width': '20%', 'height': '50vh',
                      'backgroundColor': 'white'}),

            # Div container for tabs with graphs
            html.Div([
                dcc.Tabs([
                    dcc.Tab(label='Общая ЭВ',
                            children=[dcc.Graph(id='graph',
                                                figure=figure,
                                                config=dict(responsive=True),
                                                style={'margin': '20px 40px 10px 40px',
                                                       'verticalAlign': 'middle',
                                                       'height': '55vh',
                                                       'fontFamily': 'Century Gothic, monospace',
                                                       'backgroundColor': 'white'})]),
                    dcc.Tab(label='Штаммы')
                ])
            ], style={'width': '80%'}),

        ], style={'display': 'flex', 'flex-direction': 'row',
                  'gap': '50px', 'margin': '40px 40px 0px 40px'}),

        html.Div([

            dcc.Graph(id='ve_russia',
                      figure=total_ve_russia),

            dcc.Graph(id='map',
                      figure=map_figure,
                      style={'width': '60%',
                             'height': '55vh'})
        ], style={'backgroundColor': 'white',
                  'display': 'flex', 'flex-direction': 'row', 'justify-content': 'flex-end',
                  'margin': '20px 40px 10px 40px'})

    ], style={'width': '100%',
              'height': '100vh',
              }),  # 'backgroundColor': 'white'

])

'''

dcc.Graph(id='map',
          figure=map_figure,
          style={'margin': '20px 0px 10px 40px',  # 'height': '40%',
                 'width': '40%', 'height': '55vh'}
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
    data_x = [0, 1, 2, 3, 4, 5, 6]
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
    figure.update_layout(separators=',')
    figure.update_yaxes(range=[0, data_y.max() + 0.5 * data_y.max() + ci_high.max()])

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
    csv_path = os.path.join(csv_folder_path, csv_files[date])

    subjects = get_subjects(geojson_path)
    data = extract_map_data(csv_path)
    map_data = data.iloc[:-1, :]
    ve_russia = round(data.loc[data.shape[0] - 1, column_name] * 100, 1)
    map_figure = go.Figure(go.Choroplethmapbox(
        geojson=subjects,
        locations=map_data['name'],
        featureidkey="properties.name",
        z=map_data[column_name],
        colorscale='YlGnBu',
        hovertemplate='<b> Субъект: %{location}</b><br><b> ЭВ: %{z:.1%}</b><extra></extra>'
    ))
    map_figure.update_traces(colorbar={'bgcolor': 'white',
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
    map_figure.update_layout(mapbox_style="white-bg",
                      height=1000,
                      autosize=True,
                      margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      paper_bgcolor='white',
                      plot_bgcolor='white',
                      mapbox=dict(center=dict(lat=70, lon=105), zoom=2.5),

                      )

    map_figure.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    map_figure.update_geos(fitbounds="locations")
    ve_russia_output = f'Показатель ЭВ по Российской Федерации : {str(ve_russia).replace(".", ",")} %'
    return [map_figure, ve_russia_output]
'''

if __name__ == '__main__':
    app.run_server(debug=True)
