import plotly.graph_objects as go


def plot_pie_chart(chart_data, title_text):
    if chart_data.shape[0] == 0:
        labels = ['Данные отсутствуют']
        values = [1]
        show_text = 'none'
    else:
        labels = list(chart_data['pango_lineage'].values[0].keys())
        values = list(chart_data['pango_lineage'].values[0].values())
        show_text = 'inside'
    fig = go.Figure(data=[go.Pie(labels=labels, values=values,
                                 hovertemplate="%{label}<br>%{percent}"
                                               "<extra></extra>")])
    fig.update_traces(textposition=show_text)
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide',
                      legend={'x': 0.85})
    fig.update_layout(autosize=True, separators=',',
                      template='seaborn', margin={'l': 0, 'b': 100, 't': 0, 'r': 0},
                      paper_bgcolor='white',
                      title={'text': title_text,  'x': 0.5, 'y': 0.05,
                             'xanchor': 'center', 'yanchor': 'bottom', 'font': {'size': 15}})
    return fig