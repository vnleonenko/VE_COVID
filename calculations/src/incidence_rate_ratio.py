import pandas as pd
import plotly.graph_objects as go
import numpy as np


def group_by_vac_int(df, group_columns):
    agg_fn = {}
    for column in df.columns:
        if 'count' in column:
            agg_fn.update({column: 'sum'})
        elif column == 'vac_interval_group':
            pass
        elif column in group_columns:
            agg_fn.update({column: lambda x: x.iloc[0]})
    grouped_df = df.groupby(group_columns).agg(agg_fn)
    grouped_df.reset_index(inplace=True, drop=True)
    grouped_df = grouped_df.sort_values(by=group_columns, ignore_index=True)
    return grouped_df


def read_input_data():
    vac = pd.read_csv('../output/vaccinated/vac_df.csv', encoding='cp1251', delimiter=',')
    zab = pd.read_csv('../output/infected/zab_df.csv', encoding='cp1251', delimiter=',')
    zab_vac = pd.read_csv('../output/infected_vaccinated/zab_vac_df.csv', encoding='cp1251', delimiter=',')
    pop = pd.read_csv('../output/population/pop_df.csv', encoding='cp1251', delimiter=',')

    return {'vac': vac, 'zab': zab, 'zab_vac': zab_vac, 'pop': pop}


def calc_irr(zab_vac, vac, zab, pop, case):
    vac_zab_vac_merge = vac.merge(zab_vac, on=['data_point', 'region', 'age_group',
                                               'vac_interval_group', 'vaccine'],
                                  how='left')
    vac_zab_vac_merge = group_by_vac_int(vac_zab_vac_merge, ['data_point', 'region', 'age_group', 'vaccine'])

    num = vac_zab_vac_merge[f'count_vac_{case}']
    denom = vac_zab_vac_merge['vac_count'] - vac_zab_vac_merge[f'count_vac_{case}']
    irr = vac_zab_vac_merge[['data_point', 'region', 'age_group', 'vaccine']]
    irr[f'vac_{case}'] = num
    irr[f'vac_not_{case}'] = denom
    irr[f'{case}_vac_ratio'] = num / denom

    zab_vac_zab_vac_merged = vac_zab_vac_merge.merge(zab, on=['data_point', 'region', 'age_group'])
    num = zab_vac_zab_vac_merged[f'count_{case}'] - zab_vac_zab_vac_merged[f'count_vac_{case}']
    vac_zab_pop_merged = zab_vac_zab_vac_merged.merge(pop, on=['region', 'age_group'])
    denom = vac_zab_pop_merged['population'] - vac_zab_pop_merged[f'count_{case}'] \
            - vac_zab_pop_merged['vac_count'] + vac_zab_pop_merged[f'count_vac_{case}']
    irr[f'not_vac_{case}'] = num
    irr[f'not_vac_not_{case}'] = denom
    irr[f'{case}_not_vac_ratio'] = num / denom

    irr['irr'] = irr.loc[:, f'{case}_vac_ratio'] / irr.loc[:, f'{case}_not_vac_ratio']

    return irr


def visualize_irr(irr, vaccine, subject):
    fig = go.Figure()
    ages = irr['age_group'].unique()
    t = np.linspace(0, irr.shape[0], irr.shape[0])
    for age in ages:
        y1 = irr.query(f'region == "{subject}" & vaccine == "{vaccine}" & age_group == "{age}"')['irr']
        tick_text = list(map(lambda x: '.'.join(x.split('.')[:2][::-1]), irr['data_point'].unique()))
        plot = go.Scatter(x=t, y=y1, mode='lines+markers', showlegend=True, name=age)
        fig.add_trace(plot)
        fig.update_layout(paper_bgcolor="white", yaxis_title='IRR', xaxis_title='Месяцы',
                          xaxis={'tickmode': 'array', 'tickvals': t,
                                 'ticktext': tick_text, 'tickangle': 45},
                          title={'text': f'IRR для {subject}, {vaccine}', 'x': 0.5, 'y': 0.88,
                                 'xanchor': 'center'})
    fig.write_image(f"./irr_{subject}_{vaccine}.png", engine="kaleido")


if __name__ == "__main__":
    vac_df, zab_df, zab_vac_df, pop_df = list(read_input_data().values())
    vaccine = 'SputnikV'
    subjects = ['Московская область', 'РФ', 'г. Санкт-Петербург']
    cases = ['zab', 'severe', 'hosp', 'death']
    for case in cases:
        for subject in subjects:
            irr = calc_irr(zab_vac=zab_vac_df, vac=vac_df, zab=zab_df, pop=pop_df, case=case)
            visualize_irr(irr, vaccine, subject)



