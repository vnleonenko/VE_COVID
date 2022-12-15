import plotly.graph_objects as go
import pandas as pd


def plot_vertical_bar_chart(x, y, ci, title_text):
    x_vals = [i for i in range(y.shape[0])]
    tick_text = x.dt.strftime('%m.%Y')
    bar_chart = go.Figure(data=[go.Bar(x=x_vals, y=y,
                                       width=0.5,
                                       error_y=dict(type='data',
                                                    symmetric=False,
                                                    array=ci[1],
                                                    arrayminus=ci[0],
                                                    width=4,
                                                    thickness=2),
                                       hovertemplate="<br> ЭВ: %{y:.1%}<br> ДИ: "
                                                     "+%{error_y.array:.1%} "
                                                     "/ -%{error_y.arrayminus:.1%} "
                                                     "<extra></extra>")])
    bar_chart.update_traces(marker_color='rgb(158,202,225)',
                            marker_line_color='rgb(8,48,107)',
                            marker_line_width=1.5,
                            opacity=0.6)
    bar_chart.update_layout(paper_bgcolor="white",
                            autosize=False,
                            template='plotly_white',
                            margin={'l': 30, 'b': 0, 't': 140, 'r': 20},
                            xaxis={'tickmode': 'array', 'tickvals': x_vals,
                                   'ticktext': tick_text},
                            yaxis_tickformat='.0%',
                            separators=',',
                            title={'text': title_text, 'x': 0.5, 'y': 0.88,
                                   'xanchor': 'center', 'yanchor': 'top',
                                   'font': {'size': 15}})
    return bar_chart


def plot_horizontal_bar_chart(x, y, title_text):
    bar_chart = go.Figure(data=[go.Bar(x=x, y=y,
                                       orientation='h',
                                       marker={'color': x,
                                               'colorscale': [(0, "#c4c4c4"), (0.25, "#c4c4c4"), (0.5, "#c4c4c4"),
                                                             (0.65, "#ff3333"), (0.85, "#ffff66"), (1, "#81c662")],
                                               'opacity': 0.8,
                                               'line': {'color': 'rgb(8,48,107)',
                                                        'width': 1.5}},
                                       hovertemplate="<br> ЭВ: %{x:.1%}<extra></extra>")])
    bar_chart.update_layout(template='plotly_white',
                            xaxis={'showticklabels': True, 'autorange': True},
                            xaxis_tickformat='.0%',
                            autosize=False,
                            margin={"r": 50, "t": 130, "l": 130, "b": 60})
    bar_chart.update_xaxes(zeroline=True, zerolinewidth=1, zerolinecolor='black')
    bar_chart.update_yaxes(zeroline=True, zerolinewidth=1, zerolinecolor='black')
    bar_chart.update_layout(title={'text': title_text, 'font_color': 'black',
                                   'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top',
                                   'font': {'size': 14}},
                            title_font_size=14)
    return bar_chart


def plot_int_bar_chart(data, dates, case, title_text):
    fig = go.Figure()
    vac_intervals = {'21_45_days': '21-45 дней', '45_75_days': '45-75 дней',
                     '75_90_days': '75-90 дней', '90_105_days': '90-105 дней',
                     '105_165_days': '105-165 дней', '165_195_days': '165-195 дней'}

    ve_title = 've_'+case
    cih_title = 'cih_' + case
    cil_title = 'cil_' + case

    for date in dates:
        date = date.split("_")[0].split(".")
        y = data[data['data_point'].str.contains(".".join(date))]
        inversed_date = ".".join(date[::-1])
        x = [[inversed_date for _ in range(len(vac_intervals))], list(vac_intervals.values())]
        y.reset_index(drop=True, inplace=True)
        y = pd.concat([y.iloc[2:, :], y.loc[:1, :]])
        cih = y[cih_title] - y[ve_title]
        cil = y[ve_title] - y[cil_title]
        '''cil = y[ci_titles[0]]
        y = y[column_title].fillna(0).tolist()
        cil_values = [cil_ if y_/cil_ < 2 else 2*y_ for y_, cil_ in zip(y, cil)]
        cil_points = [i-j for i, j in zip(y, cil_values)]'''
        '''y_ = y[column_title].tolist()
        cil_ = y[ci_titles[0]].tolist()
        cil_ = [j if j/i < 2 else 2*i for i, j in zip(y_, cil_)]
        print([j if j/i < 2 else 2*i for i, j in zip(y_, cil_)])
        print(cil_)
        print([j/i for i, j in zip(y_, cil_)])
        print('y', y[column_title], '\n', 'cil', y[ci_titles[0]], '\n', 'cih', y[ci_titles[1]])
        cil = [i - j for i, j in zip(y_, cil_)]'''

        bar_chart = go.Bar(x=x, y=y[ve_title], width=0.6, showlegend=False,
                           marker={'color': y[ve_title],
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
        fig.update_xaxes(tickfont={'size': 10})
        fig.update_yaxes(tickformat='.0%')
        fig.update_layout(autosize=False, separators=',', template='plotly_white',
                          margin={'l': 30, 'b': 25, 't': 90, 'r': 20},
                          title={'text': title_text, 'x': 0.5, 'y': 0.95,
                                 'xanchor': 'center', 'yanchor': 'top',
                                 'font': {'size': 15}})
    return fig


def plot_int_bar_chart2(data, dates, case, title_text):
    fig = go.Figure()
    vac_intervals = {'21_45_days': '21-45 д.', '45_75_days': '45-75 д.',
                     '75_90_days': '75-90 д.', '90_105_days': '90-105 д.',
                     '105_165_days': '105-165 д.', '165_195_days': '165-195 д.'}
    for date in dates:
        date = date.split("_")[0].rstrip('.B').split(".")
        y = data[data['data_point'].str.contains(".".join(date))]
        inversed_date = ".".join(date[::-1])
        x = [[inversed_date for _ in range(len(vac_intervals))], list(vac_intervals.values())]
        y.reset_index(drop=True, inplace=True)
        y = pd.concat([y.iloc[2:, :], y.loc[:1, :]])
        y = y[['ve_'+case, 'cil_'+case, 'cih_'+case]]
        cih = y['cih_'+case] - y['ve_'+case]
        cil = y['ve_'+case] - y['cil_'+case]

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
        fig.update_xaxes(tickfont={'size': 10})
        fig.update_yaxes(tickformat='.0%')
        fig.update_layout(autosize=False, separators=',', template='plotly_white',
                          margin={'l': 30, 'b': 25, 't': 90, 'r': 20},
                          title={'text': title_text, 'x': 0.5, 'y': 0.95,
                                  'xanchor': 'center', 'yanchor': 'top',
                                  'font': {'size': 12}})
    return fig
