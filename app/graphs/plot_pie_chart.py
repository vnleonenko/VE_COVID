import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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
                      legend={'x': 0.87})
    fig.update_layout(autosize=True, separators=',',
                      template='seaborn', margin={'l': 0, 'b': 100, 't': 0, 'r': 0},
                      paper_bgcolor='white',
                      title={'text': title_text,  'x': 0.5, 'y': 0.07,
                             'xanchor': 'center', 'yanchor': 'bottom', 'font': {'size': 15}})
    return fig


def plot_strains_and_ve(strains_df, ve_df, case, age, title):
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.05, shared_xaxes=True)
    x = strains_df['collection_date'].unique()
    y = ve_df[ve_df['age_group'] == age][f've_' + case].tolist()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='ЭВ',
                             hovertemplate="ЭВ: %{y:.0%}<extra></extra>"),
                  row=1, col=1)
    for i in range(x.shape[0]):
        fig.add_annotation(x=x[i],
                           y=y[i],
                           text=str(round(y[i] * 100)) + '%',
                           showarrow=True,
                           row=1, col=1)
    fig.add_trace(go.Scatter(
        name='Upper Bound',
        x=strains_df['collection_date'].unique(),  # x, then x reversed
        y=ve_df[ve_df['age_group'] == age][f'cih_' + case].tolist(),
        hovertemplate="ДИ+: %{y:.0%}<extra></extra>",
        marker=dict(color="#444"),
        line=dict(width=0),
        mode='lines',
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty',
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        name='Lower Bound',
        x=strains_df['collection_date'].unique(),
        y=ve_df[ve_df['age_group'] == age][f'cil_' + case].tolist(),
        marker=dict(color="#444"),
        hovertemplate="ДИ-: %{y:.0%}<extra></extra>",
        line=dict(width=0),
        mode='lines',
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty',
        showlegend=False
    ))
    fig.add_trace(go.Scatter(x=strains_df['collection_date'].unique(),
                             y=[0.5 for i in range(strains_df['collection_date'].unique().shape[0])],
                             mode='lines',
                             name='50% порог ЭВ',
                             hovertemplate="ЭВ: %{y:.0%}<extra></extra>",
                             line=dict(dash='dash', color='green'),
                             connectgaps=True, ),
                  row=1, col=1)

    color_ind = 0
    for key in strains_df['keys'].unique():
        data = strains_df[strains_df['keys'] == key]
        color_palette = px.colors.qualitative.Pastel1 + px.colors.qualitative.Pastel2
        fig.add_trace(
            go.Bar(x=sorted(data['collection_date'].tolist(), key=lambda x: list(map(int, x.split('-')))),
                   y=data['values'],
                   name=key,
                   marker={'color': color_palette[color_ind]},
                   text=data['keys'],
                   textangle=0,
                   texttemplate='%{text} <br>%{y:.1%}',
                   hovertemplate="%{text}<br>%{y:.1%}<extra></extra>"
                   ), row=2, col=1)
        color_ind += 1
        fig.update_layout(uniformtext_minsize=9, uniformtext_mode='hide')

    fig.update_layout(template='simple_white', barmode='stack', bargap=0,
                      title={'text': title, 'xanchor': 'center', 'yanchor': 'top',
                            'font': {'size': 11}, 'x': 0.5, 'y': 0.97})
    if ve_df[f'cil_'+case].min() < -0.5:
        fig.update_yaxes(title_text="Эффективность вакцинации", tickformat=',.0%',
                         tick0=0.5, dtick=0.5, range=[-1, 1], row=1, col=1)
    else:
        fig.update_yaxes(title_text="Эффективность вакцинации", tickformat=',.0%',
                         tick0=0.5, dtick=0.25, row=1, col=1)
    fig.update_yaxes(title_text="Соотношение \nштаммов", range=[0, 1], tickformat=',.0%', row=2, col=1)

    fig.update_xaxes(showticklabels=False, ticks='inside', ticklen=0.1, row=1, col=1)
    fig.update_xaxes(title='Месяцы',  type='category', categoryorder='category ascending',
                     tickvals=x, ticktext=['.'.join(date.split('-')[::-1]) for date in x],
                     row=2, col=1)
    fig.update_layout(margin=dict(l=20, r=20, t=80, b=20))
    return fig
