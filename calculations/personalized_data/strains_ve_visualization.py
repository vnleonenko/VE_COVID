import numpy as np
import pandas as pd

import plotly.express as px

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def calc_virus_ratio(virus_titles: list):
    virus_types_ratio = {}
    for title in virus_titles:
        if title in list(virus_types_ratio.keys()):
            virus_types_ratio[title] += 1
        else:
            virus_types_ratio[title] = 1
    virus_types_ratio = {k: round(v / len(virus_titles), 5) for k, v in virus_types_ratio.items()}
    return virus_types_ratio


def get_strain_data(csv_path):
    strain_data = pd.read_csv(csv_path)
    filtered_data = strain_data.loc[:, ['location', 'collection_date',
                                        'pango_lineage', 'pangolin_version', 'variant',
                                        'latitude', 'longitude', 'city', 'subject', 'district']]

    filtered_data['collection_date'] = filtered_data['collection_date'].map(lambda x: x.rsplit('-', 1)[0])
    grouped_data = filtered_data.groupby(['collection_date', 'city',
                                          'subject', 'district']).agg({'location': lambda x: x.iloc[0],
                                                                       'pango_lineage': lambda x: list(x),
                                                                       'pangolin_version': lambda x: list(x),
                                                                       'variant': lambda x: x.iloc[0],
                                                                       'latitude': lambda x: x.iloc[0],
                                                                       'longitude': lambda x: x.iloc[0]})
    grouped_data.reset_index(inplace=True)
    agg_rf = grouped_data.groupby('collection_date', as_index=False).agg({'city': lambda x: 'Russia',
                                                                          'subject': lambda x: 'Russian Federation',
                                                                          'district': lambda x: '--',
                                                                          'location': lambda x: '--',
                                                                          'pango_lineage': lambda x: sum(x, []),
                                                                          'pangolin_version': lambda x: sum(x, []),
                                                                          'variant': lambda x: x.iloc[0],
                                                                          'latitude': lambda x: '--',
                                                                          'longitude': lambda x: '--'})
    grouped_data = pd.concat([grouped_data, agg_rf])
    grouped_data.reset_index(inplace=True, drop=True)
    grouped_data.sort_values(by='collection_date', inplace=True)
    grouped_data['pango_lineage'] = grouped_data['pango_lineage'].apply(calc_virus_ratio)
    grouped_data['pangolin_version'] = grouped_data['pangolin_version'].apply(calc_virus_ratio)
    return grouped_data


data = get_strain_data('../../app/data/strains/20221020-MH93845-490.csv')
subjects = ['Russian Federation', 'Saint Petersburg']  # Moscow
strains = data[(data['subject'].isin(subjects)) & (data['collection_date'].str.contains('2022'))]
subject_data = strains[strains['subject'] == 'Russian Federation']
melted_dict = pd.DataFrame(pd.DataFrame(subject_data['pango_lineage']   \
                                        .values.tolist()).stack().reset_index(level=1))
melted_dict.columns = ['keys', 'values']
subject_data = pd.merge(subject_data.reset_index(drop=True), melted_dict,
                        left_index=True, right_index=True)
subject_data = subject_data[~subject_data['keys'].isin(['Unassigned', np.nan])]
subject_data.loc[subject_data['values'] < 0.05, 'keys'] = 'other'
subject_data = subject_data.groupby(['collection_date', 'keys'], as_index=False).sum()


ve_df = pd.read_csv('../../../misc/ve_2022.csv', encoding='utf-8', delimiter=';')
ve_df['region'] = 'Russian Federation'

cases = ['zab', 'hosp', 'severe', 'death']
ages = ['18-59', '60+']

for case in cases:
    for age in ages:
        fig = make_subplots(rows=2, cols=1, vertical_spacing=0.03, shared_xaxes=True,)
        x = subject_data['collection_date'].unique()
        y = ve_df[ve_df['age_group'] == age][f've_'+case].tolist()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='ЭВ'),
                      row=1, col=1)
        for i in range(x.shape[0]):
            fig.add_annotation(x=x[i],
                               y=y[i],
                               text=str(round(y[i]*100))+'%',
                               showarrow=True,
                               row=1, col=1)
        fig.add_trace(go.Scatter(
            name='Upper Bound',
            x=subject_data['collection_date'].unique(),  # x, then x reversed
            y=ve_df[ve_df['age_group'] == age][f'cih_'+case].tolist(),
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            name='Lower Bound',
            x=subject_data['collection_date'].unique(), # x, then x reversed
            y=ve_df[ve_df['age_group'] == age][f'cil_'+case].tolist(),
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        ))
        fig.add_trace(go.Scatter(x=subject_data['collection_date'].unique(),
                                 y=[0.5 for i in range(subject_data['collection_date'].unique().shape[0])],
                                 mode='lines',
                                 name='50% порог ЭВ',
                                 line=dict(dash='dash', color='green'),
                                 connectgaps=True,),
                      row=1, col=1)

        color_ind = 0
        for key in subject_data['keys'].unique():
            data = subject_data[subject_data['keys'] == key]
            color_palette = px.colors.qualitative.Pastel1 # Set3

            fig.add_trace(go.Bar(x=sorted(data['collection_date'].tolist(), key=lambda x: list(map(int, x.split('-')))),
                                 y=data['values'],
                                 name=key,
                                 marker={'color': color_palette[color_ind]},
                                 text=data['keys'],
                                 texttemplate='%{text} <br>%{y:.1%}',
                                 ), row=2, col=1)
            color_ind += 1
            # fig.update_traces(textposition='inside', row=2, col=1)
            fig.update_layout(uniformtext_minsize=9, uniformtext_mode='hide')

        fig.update_layout(template='simple_white', barmode='stack', bargap=0)
        fig.update_yaxes(title_text="Эффективность вакцинации",  tickformat=',.0%',
                         tick0=0.5, dtick=0.25, row=1, col=1)
        fig.update_yaxes(title_text="Соотношение \nШтаммов", range=[0, 1],
                         tickformat=',.0%', row=2, col=1)
        fig.update_xaxes(showticklabels=False, ticks='inside',
                         ticklen=0.1, row=1, col=1)
        fig.update_xaxes(title='Месяцы',
                         type='category',
                         categoryorder='category ascending',
                         tickvals=x,
                         ticktext=['.'.join(date.split('-')[::-1]) for date in x],
                         row=2, col=1)
        fig.update_layout(width=1000, height=800)   # , height=1100
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))

        fig.write_image(f'./output/ve_and_strains/fig_{case}_{age}.png')
