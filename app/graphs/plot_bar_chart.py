import plotly.graph_objects as go


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
                                       hovertemplate="<br> ЭВ: %{y:.1%}<br> ДИ+ "
                                                     "%{error_y.array:.1%}"
                                                     "<br> ДИ- %{error_y.arrayminus:.1%} "
                                                     "<extra></extra>")])
    bar_chart.update_traces(marker_color='rgb(158,202,225)',
                            marker_line_color='rgb(8,48,107)',
                            marker_line_width=1.5,
                            opacity=0.6)
    bar_chart.update_layout(paper_bgcolor="white",
                            template='none',
                            margin={'l': 50, 'b': 20, 't': 110, 'r': 20},
                            xaxis={'tickmode': 'array', 'tickvals': x_vals, 'ticktext': tick_text},
                            yaxis_tickformat='.0%',
                            separators=',',
                            title={'text': title_text, 'x': 0.5, 'y': 0.9,
                                   'xanchor': 'center', 'yanchor': 'top'})
    return bar_chart


def plot_horizontal_bar_chart(x, y, title_text):
    bar_chart = go.Figure(data=[go.Bar(x=x, y=y,
                                       orientation='h',
                                       marker={'color': x,
                                               'colorscale': [(0, "#9ecae1"), (1, "#81c662")],
                                               'opacity': 0.8,
                                               'line': {'color': 'rgb(8,48,107)',
                                                        'width': 1.5}},
                                       hovertemplate="<br> ЭВ: %{x:.1%}<extra></extra>")])
    bar_chart.update_layout(template='plotly_white',
                            xaxis={'showticklabels': True},
                            xaxis_tickformat='.0%',
                            autosize=True,
                            margin={"r": 50, "t": 130, "l": 130, "b": 0})
    bar_chart.update_xaxes(zeroline=True, zerolinewidth=1, zerolinecolor='black')
    bar_chart.update_yaxes(zeroline=True, zerolinewidth=1, zerolinecolor='black')
    bar_chart.update_layout(title={'text': title_text, 'font_color': 'black',
                                     'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                            title_font_size=14)
    return bar_chart


