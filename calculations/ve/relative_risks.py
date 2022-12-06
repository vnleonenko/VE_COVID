from plotly.subplots import make_subplots
import numpy as np
import plotly.graph_objects as go


vaccines_en_ru = {'AllVaccines': 'Все вакцины',
                  'SputnikV': 'Спутник V',
                  'SputnikLite': 'Спутник Лайт',
                  'CoviVac': 'КовиВак',
                  'EpiVacCorona': 'ЭпиВак'}


def compute_relative_risks(inf_vac_df):
    agg_dict = {}
    columns_to_groupby = ['data_point', 'region', 'vaccine']
    for agg_column in inf_vac_df.columns:
        if agg_column in columns_to_groupby or 'vac' not in agg_column:
            agg_dict.update({agg_column: lambda x: x.iloc[0]})
        else:
            agg_dict.update({agg_column: 'sum'})
    inf_vac_df = inf_vac_df.groupby(columns_to_groupby).agg(agg_dict)

    inf_vac_df.drop('vac_interval_group', axis=1, inplace=True)
    inf_vac_df.reset_index(drop=True, inplace=True)
    cases = ['hosp', 'severe', 'death']
    ages = ['_18_59', '_60', '_total']
    or_df = inf_vac_df.loc[:, ['data_point', 'region', 'vaccine']]
    for age in ages:
        for case in cases:
            or_column = 'or_'+case+age
            inf_vac_zab = 'count_vac_zab'+age
            inf_vac_case = 'count_vac_'+case+age
            inf_zab = 'count_zab'+age
            inf_case = 'count_'+case+age
            cih = 'cih_'+case+age
            cil = 'cil_'+case+age
            a = inf_vac_df[inf_vac_case]
            b = inf_vac_df[inf_vac_zab]
            c = inf_vac_df[inf_case]
            d = inf_vac_df[inf_zab]
            or_df[or_column] = (a/(a+b)) / (c/(c+d))
            or_df[cih] = np.exp(np.log(or_df[or_column]) + 1.96*np.sqrt((1-a/(a+b))/a + (1-(c/(c+d)))/c))
            or_df[cil] = np.exp(np.log(or_df[or_column]) - 1.96*np.sqrt((1-a/(a+b))/a + (1-(c/(c+d)))/c))
    or_df.replace(np.inf, 0, inplace=True)
    return or_df


def visualize_relative_risks(df, vaccine, subject):
    data_points = df['data_point'].unique()
    figure = make_subplots(rows=1, cols=3, y_title='Относительный риск',
                           subplot_titles=('Относительный риск госпитализации',
                                           'Относительный риск тяжелого исхода',
                                           'Относительный риск летального исхода'))
    tick_text = [data_point.split('_')[0].split('.')[::-1] for data_point in data_points]
    x = [i for i in range(len(data_points))]
    cases = ['hosp', 'severe', 'death']
    ages = ['_18_59', '_60', '_total']
    title_text = f'Риски для населения {subject} ({vaccines_en_ru[vaccine]})'
    colors = ['blue', 'red', 'green']
    for i in range(len(cases)):
        for j in range(len(ages)):
            title = ''
            if ages[j] == '_18_59':
                title = 'от 18 до 59 лет'
            elif ages[j] == '_60':
                title = 'от 60 лет и старше'
            elif ages[j] == '_total':
                title = 'от 18 лет и старше'

            show_legend = True
            if i != 0:
                show_legend = False
            column = 'or_'+cases[i]+ages[j]
            cih_title = 'cih_'+cases[i]+ages[j]
            cil_title = 'cil_'+cases[i] + ages[j]
            df = df.query(f'vaccine == "{vaccine}" & region == "{subject}"')
            df.reset_index(drop=True, inplace=True)
            y, cih, cil = df[column], df[cih_title], df[cil_title]
            figure.add_traces(go.Scatter(x=x, y=y,
                                         error_y=dict(type='data',
                                         symmetric=False,
                                         array=cih-y,
                                         arrayminus=y-cil,
                                         width=4,
                                         thickness=2),
                                         marker_color=colors[j],
                                         mode='lines+markers',
                                         showlegend=show_legend,
                                         name=title), 1, i+1)
            figure.update_xaxes(tickmode='array', tickvals=x, ticktext=tick_text)
            figure.update_layout(title_text=title_text, paper_bgcolor="white", template='none',
                                 height=500, width=1500)

    figure.write_image(f"./риски_{subject}_{vaccines_en_ru[vaccine]}.png", engine="kaleido")
