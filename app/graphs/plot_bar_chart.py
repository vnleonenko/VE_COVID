import plotly.graph_objects as go
import pandas as pd
import locale


locale.setlocale(locale.LC_TIME, 'ru_RU')


def generate_colorscale(y):
    negative_y = sum(abs(y[y < 0]))
    positive_y = sum(y[y > 0])
    if positive_y == 0 and negative_y == 0:
        colorscale = [(0, "#c4c4c4"), (1, "#c4c4c4")]
    elif negative_y == 0:
        colorscale = [(0, '#ff3333'),
                      (0.5, "#ffff66"),
                      (1, "#81c662")]
    else:
        gray_color_ratio = round(negative_y / (negative_y + positive_y), 2)
        pos_colors_ratio = (1 - round(gray_color_ratio, 3)) / 3
        red_color_ratio = round(gray_color_ratio + pos_colors_ratio, 3)
        yellow_color_ratio = round(red_color_ratio + pos_colors_ratio, 3)
        colorscale = [(0, "#c4c4c4"),
                      (gray_color_ratio, "#c4c4c4"),
                      (red_color_ratio, '#ff3333'),
                      (yellow_color_ratio, "#ffff66"),
                      (1, "#81c662")]
    return colorscale


def plot_vertical_bar_chart(x, y, ci, title_text):
    bar_chart = go.Figure(data=[go.Bar(x=x, y=y,
                                       error_y=dict(type='data',
                                                    symmetric=False,
                                                    array=ci[1],
                                                    arrayminus=ci[0],
                                                    thickness=1.6),
                                       hovertemplate="<br> ЭВ: %{y:.1%}<br> ДИ: "
                                                     "+%{error_y.array:.1%} "
                                                     "/ -%{error_y.arrayminus:.1%} "
                                                     "<extra></extra>")])
    bar_chart.update_traces(marker_color='rgb(158,202,225)',
                            marker_line_color='rgb(8,48,107)',
                            marker_line_width=1.5,
                            opacity=0.6)
    bar_chart.update_xaxes(tickformat='%m.%Y')
    bar_chart.update_layout(paper_bgcolor="white",
                            autosize=False,
                            template='plotly_white',
                            margin={'l': 30, 'b': 0, 't': 140, 'r': 20},
                            yaxis_tickformat='.0%',
                            separators=',',
                            title={'text': title_text, 'x': 0.5, 'y': 0.92,
                                   'xanchor': 'center', 'yanchor': 'top',
                                   'font': {'size': 12}})
    bar_chart.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=6,
                         label="6м",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="1г",
                         step="year",
                         stepmode="todate"),
                    dict(label="все",
                         step="all")]),
                yanchor='middle'
            ),
            type="date"))
    return bar_chart


def plot_horizontal_bar_chart(x, y, title_text):
    bar_chart = go.Figure(data=[go.Bar(x=x, y=y,
                                       orientation='h',
                                       marker={'color': x,
                                               'colorscale': generate_colorscale(x),
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
                                   'y': 0.92, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top',
                                   'font': {'size': 12}})
    return bar_chart


def plot_int_bar_chart(data, dates, case, title_text):
    fig = go.Figure()
    vac_intervals = {'21_45_days': '21-45 дней', '45_75_days': '45-75 дней',
                     '75_90_days': '75-90 дней', '90_105_days': '90-105 дней',
                     '105_165_days': '105-165 дней', '165_195_days': '165-195 дней'}
    ve_title = 've_' + case
    cih_title = 'cih_' + case
    cil_title = 'cil_' + case

    for date in dates:
        date = date.split("_")[0].split(".")
        y = data[data['data_point'].str.contains(".".join(date))]
        inverse_date = ".".join(date[::-1])
        x = [[inverse_date for _ in range(len(vac_intervals))], list(vac_intervals.values())]
        y.reset_index(drop=True, inplace=True)
        y = pd.concat([y.iloc[2:, :], y.loc[:1, :]])
        cih = y[cih_title] - y[ve_title]
        cil = y[ve_title] - y[cil_title]
        bar_chart = go.Bar(x=x, y=y[ve_title], width=0.6, showlegend=False,
                           marker={'color': y[ve_title],
                                   'colorscale': generate_colorscale(y[ve_title]),
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
                          title={'text': title_text, 'x': 0.5, 'y': 0.92,
                                 'xanchor': 'center', 'yanchor': 'top',
                                 'font': {'size': 12}})
    return fig


def plot_int_bar_chart2(data, dates, case, title_text):
    fig = go.Figure()
    vac_intervals = {'21_45_days': '21-45 дней', '45_75_days': '45-75 дней',
                     '75_90_days': '75-90 дней', '90_105_days': '90-105 дней',
                     '105_165_days': '105-165 дней', '165_195_days': '165-195 дней'}
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
                                   'colorscale': generate_colorscale(y['ve_'+case]),
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
                          title={'text': title_text, 'x': 0.5, 'y': 0.92,
                                  'xanchor': 'center', 'yanchor': 'top',
                                  'font': {'size': 12}})
    return fig
