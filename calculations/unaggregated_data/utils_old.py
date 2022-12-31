import zipfile
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import matplotlib


def unzip_archive(zip_path, dest_folder):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(f'./{dest_folder}', pwd=b'y6w09W8')


def read_file(file_path):
    return pd.read_table(file_path)


def count_healthy_sample(data):
    num_records_data = data.groupby('id', as_index=False).size().sort_values(by='size')
    one_record_ids = num_records_data[num_records_data['size'] == 1]
    data_w_one_record = data[data['id'].isin(one_record_ids['id'].tolist())]
    data_w_one_record_feb = data_w_one_record[data_w_one_record['event_date'].str.contains('2022-02')]
    healthy_sample_ids = data_w_one_record_feb['id']
    healthy_sample = data_w_one_record_feb.groupby(['region_id', 'age_cat', 'tyazh_code'], as_index=False).size()
    grouped_healthy_subsample = healthy_sample.groupby(['region_id', 'tyazh_code'],
                                                    as_index=False).agg({'region_id': lambda x: x.iloc[0],
                                                                         'age_cat': lambda x: 'all',
                                                                         'size': 'sum'})
    healthy_sample = pd.concat([healthy_sample, grouped_healthy_subsample])
    healthy_sample = healthy_sample[(healthy_sample['age_cat'] != 0) &
                                       (healthy_sample['tyazh_code'] != 0)]
    sum_res = healthy_sample.groupby(['region_id', 'age_cat'], as_index=False).agg({'size': 'sum'})
    healthy_sample = healthy_sample.merge(sum_res, on=['region_id', 'age_cat'], how='left',
                                             suffixes=('_tyazh', '_total'))
    healthy_sample['ratio'] = healthy_sample['size_tyazh'] / healthy_sample['size_total']
    return healthy_sample, healthy_sample_ids


def get_fully_vaccinated_ids(dataframe):
    inf_vac_df = dataframe.groupby(['id', 'event_type'], as_index=False).size()
    inf_vac_ids = inf_vac_df[inf_vac_df['event_type'] == 'i']['id'].tolist()
    only_vac_ids = dataframe[~dataframe['id'].isin(inf_vac_ids)]['id'].tolist()
    return only_vac_ids


def count_fully_vac_sample(inf_df, ids):
    fully_vac_feb = inf_df[inf_df['id'].isin(ids)]
    fully_vac_sample = fully_vac_feb.groupby(['region_id', 'age_cat', 'tyazh_code'], as_index=False).size()
    grouped_vac_sample = fully_vac_sample.groupby(['region_id', 'tyazh_code'],
                                                  as_index=False).agg({'region_id': lambda x: x.iloc[0],
                                                                       'age_cat': lambda x: 'all',
                                                                       'size': 'sum'})
    fully_vac_sample = pd.concat([fully_vac_sample, grouped_vac_sample])
    fully_vac_sample = fully_vac_sample[(fully_vac_sample['age_cat'] != 0) &
                                        (fully_vac_sample['tyazh_code'] != 0)]
    sum_res = fully_vac_sample.groupby(['region_id', 'age_cat'], as_index=False).agg({'size': 'sum'})
    fully_vac_sample = fully_vac_sample.merge(sum_res, on=['region_id', 'age_cat'], how='left',
                                              suffixes=('_tyazh', '_total'))
    fully_vac_sample['ratio'] = fully_vac_sample['size_tyazh'] / fully_vac_sample['size_total']
    return fully_vac_sample


def get_inf_vac_ids(dataframe):
    last_event_int = [6, 9, 12, 15]
    res_dict = {}
    for i in range(len(last_event_int)):
        right_bound = last_event_int[i]
        if i == 0:
            left_bound = '<'
            ids = dataframe[(dataframe['months_diff'] < right_bound)]['id']
            res_dict.update({f'{left_bound}{str(right_bound)}': ids.tolist()})
        elif i == len(last_event_int)-1:
            left_bound = last_event_int[i - 1]
            ids = dataframe[(dataframe['months_diff'] >= left_bound) &
                            (dataframe['months_diff'] < right_bound)]['id']
            res_dict.update({f'{str(left_bound)}{str(right_bound)}': ids.tolist()})
            ids = dataframe[(dataframe['months_diff'] >= right_bound)]['id']
            res_dict.update({f'>={str(right_bound)}': ids.tolist()})
        else:
            left_bound = last_event_int[i - 1]
            ids = dataframe[(dataframe['months_diff'] >= left_bound) &
                            (dataframe['months_diff'] < right_bound)]['id']
            res_dict.update({f'{str(left_bound)}-{str(right_bound)}': ids.tolist()})
    return res_dict


def count_inf_vac_sample(inf_df, ids):
    inf_vac_feb = inf_df[inf_df['id'].isin(ids)]
    inf_vac_sample = inf_vac_feb.groupby(['region_id', 'age_cat', 'tyazh_code'], as_index=False).size()
    grouped_inf_vac_sample = inf_vac_sample.groupby(['region_id', 'tyazh_code'],
                                                    as_index=False).agg({'region_id': lambda x: x.iloc[0],
                                                                       'age_cat': lambda x: 'all',
                                                                       'size': 'sum'})
    inf_vac_sample = pd.concat([inf_vac_sample, grouped_inf_vac_sample])
    inf_vac_sample = inf_vac_sample[(inf_vac_sample['age_cat'] != 0) &
                                    (inf_vac_sample['tyazh_code'] != 0)]
    sum_res = inf_vac_sample.groupby(['region_id', 'age_cat'], as_index=False).agg({'size': 'sum'})
    inf_vac_sample = inf_vac_sample.merge(sum_res, on=['region_id', 'age_cat'], how='left',
                                          suffixes=('_tyazh', '_total'))
    inf_vac_sample['ratio'] = inf_vac_sample['size_tyazh'] / inf_vac_sample['size_total']
    return inf_vac_sample


def add_period_from_last_record(df, inf_feb):
    last_records = df.groupby(by='id').agg({'id': lambda x: x.iloc[-1],
                                          'event_date': lambda x: x.iloc[-1],
                                          'event_type': lambda x: x.iloc[-1],
                                          'age_cat': lambda x: x.iloc[-1],
                                          'region_id': lambda x: x.iloc[-1],
                                          'vaccine_code': lambda x: x.iloc[-1],
                                          'stage_number': lambda x: x.iloc[-1],
                                          'tyazh_code': lambda x: x.iloc[-1]})

    last_records = last_records.merge(inf_feb[['id', 'event_date', 'event_type']],
                                      on='id', how='inner', suffixes=('_lr', '_feb'))
    last_records['event_date_lr'] = pd.to_datetime(last_records['event_date_lr'],
                                                             errors='coerce', format='%Y-%m-%d')
    last_records['event_date_feb'] = pd.to_datetime(last_records['event_date_feb'],
                                                              errors='coerce', format='%Y-%m-%d')
    infection_date = last_records['event_date_feb'].dt.date
    last_vac_date = last_records['event_date_lr'].dt.date

    last_records['months_diff'] = (infection_date - last_vac_date) / np.timedelta64(1, 'M')
    return last_records


"""def plot_ratio(healthy_sample, fully_vac_sample, inf_vac_sample, subject_id, age_cats, region_ids):
    colors = px.colors.qualitative.Plotly
    severe_degree = {1: 'удовл.', 2: 'средней тяж.',
                     3: 'тяж.', 4: 'крайне тяж.',
                     5: 'кл. смерть', 6: 'терм.'}
    df_titles = {0: 'невакцинированные',
                 1: 'вакцинированные',
                 2: 'заболевшие и вакцинированные(до 6 месяцев)'}
    '''3: 'заболевшие и вакцинированные(от 3 до 6 месяцев)',
    4: 'заболевшие и вакцинированные(от 6 до 9 месяцев)',
    5: 'заболевшие и вакцинированные(от 9 до 12 месяцев)',
    6: 'заболевшие и вакцинированные(от 12 до 15 месяцев)'''

    fig = make_subplots(rows=2, cols=2, vertical_spacing=0.06, shared_yaxes=True,
                        subplot_titles=('Категория 20-29 лет', 'Категория 60-69 лет'))
    fig.update_layout(title={'text': f"Доля заболевших в феврале с разной степенью тяжести "
                                     f"({region_ids[region_ids['region_id']==subject_id]['short_name'].values[0]})",
                             'x': 0.5})
    show_legend = True
    for i, age_cat in enumerate(age_cats):
        max_cut_value = healthy_sample[(healthy_sample['age_cat'].isin(age_cats)) &
                                       (healthy_sample['region_id'] == subject_id)]['ratio'].max()
        min_cut_value1 = healthy_sample[(healthy_sample['age_cat'].isin(age_cats)) &
                                       (healthy_sample['tyazh_code'] == 2) &
                                       (healthy_sample['region_id'] == subject_id)]['ratio'].max()
        min_cut_value2 = fully_vac_sample[(fully_vac_sample['age_cat'].isin(age_cats)) &
                                        (fully_vac_sample['tyazh_code'] == 2) &
                                        (fully_vac_sample['region_id'] == subject_id)]['ratio'].max()
        min_cut_value3 = inf_vac_sample[(inf_vac_sample['age_cat'].isin(age_cats)) &
                                        (inf_vac_sample['tyazh_code'] == 2) &
                                        (inf_vac_sample['region_id'] == subject_id)]['ratio'].max()
        if min_cut_value1 > min_cut_value2 and min_cut_value1 > min_cut_value3:
            min_cut_value = min_cut_value1
        elif min_cut_value2 > min_cut_value1 and min_cut_value2 > min_cut_value3:
            min_cut_value = min_cut_value2
        else:
            min_cut_value = min_cut_value3
        cut_interval = [min_cut_value+0.15*min_cut_value, max_cut_value-0.15*max_cut_value]

        for j, df in enumerate([healthy_sample, fully_vac_sample, inf_vac_sample]):
            region_df = df[df['region_id'] == subject_id]
            df = region_df[region_df['age_cat'] == age_cat]
            x1, y1 = df['tyazh_code'], df['ratio']
            tick_text = [severe_degree[x] for x in x1]
            if i != 0:
                show_legend = False
            fig.add_trace(go.Bar(x=x1,
                                 y=y1,
                                 name=df_titles[j],
                                 showlegend=show_legend,
                                 marker_color=colors[j]), row=2, col=i+1)

            fig.add_trace(go.Bar(x=x1,
                                 y=y1,
                                 name=df_titles[j],
                                 marker_color=colors[j],
                                 showlegend=False), row=1, col=i+1)

            fig.update_yaxes(range=[cut_interval[1],  1], row=1, col=i+1)
            fig.update_xaxes(visible=False, row=1, col=i+1)
            fig.update_yaxes(range=[0, cut_interval[0]], row=2, col=i+1)

    fig.update_xaxes(tickmode='array', tickvals=list(severe_degree.keys()), ticktext=list(severe_degree.values()))
    fig.update_yaxes(showdividers=True)
    fig.update_layout(autosize=False, width=1000, height=800)
    fig.write_image(f"./ratio_{subject_id}_age_{'_'.join(list(map(str, age_cats)))}_3_groups.png",
                    engine="kaleido")"""


font = {'size': 8}

matplotlib.rc('font', **font)


def plot_ratio_plt(dfs, subject_id, age_cats, region_ids, df_titles):
    severe_degree = {1: 'удовл.', 2: 'средней тяж.',
                     3: 'тяж.', 4: 'крайне тяж.',
                     5: 'кл. смерть', 6: 'терм.'}

    age_groups = {'2': '20-29', '6': '60-69'}

    for i, age_cat in enumerate(age_cats):
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
        fig.subplots_adjust(hspace=0.05)
        title = f"Доля заболевших в феврале с разной степенью тяжести \n" \
                f"({region_ids[region_ids['region_id'] == subject_id]['short_name'].values[0]}," \
                f" категория {age_groups[age_cat]} лет)"

        min_cut_value = 0
        max_cut_value = 0
        for df in dfs:
            max_cut = df[(df['age_cat'].isin(age_cats)) & (df['tyazh_code'] == 1) &
                         (df['region_id'] == subject_id)]['ratio'].min()
            min_cut = df[(df['age_cat'].isin(age_cats)) & (df['tyazh_code'] == 2) &
                         (df['region_id'] == subject_id)]['ratio'].max()

            if min_cut > min_cut_value:
                min_cut_value = min_cut
            if max_cut > max_cut_value:
                max_cut_value = max_cut

        cut_interval = [min_cut_value + 0.2 * min_cut_value, max_cut_value - 0.25 * max_cut_value]
        x_max = 0
        offset = 0
        for j, df in enumerate(dfs):
            region_df = df[df['region_id'] == subject_id]
            df = region_df[region_df['age_cat'] == age_cat]
            x, y = df['tyazh_code'], df['ratio']
            width = 0.5
            if len(x) > x_max:
                x_max = len(x)
            bar_width = width / len(dfs)
            center = int(len(dfs)/2)

            if len(dfs) % 2 != 0:
                if j < center:
                    offset = -(center-j) * bar_width
                elif j == center:
                    offset = 0
                else:
                    offset = (j-center) * bar_width
            else:
                if j < center:
                    offset = -(center-j) * bar_width + bar_width/2
                elif j >= center:
                    offset = (j-center) * bar_width + bar_width/2

            ax1.bar(x + offset, y, bar_width, label=df_titles[j])
            ax2.bar(x + offset, y, bar_width)

        ax1.set_ylim(cut_interval[1], 1)
        ax2.set_ylim(0, cut_interval[0])

        # hide the spines between ax and ax2
        ax1.spines.bottom.set_visible(False)
        ax2.spines.top.set_visible(False)
        ax1.xaxis.tick_top()
        ax1.tick_params(labeltop=False)  # don't put tick labels at the top
        ax2.xaxis.tick_bottom()
        ax1.set_title(title)
        ax1.legend()

        d = .5  # proportion of vertical to horizontal extent of the slanted line
        kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
                      linestyle="none", color='k', mec='k', mew=1, clip_on=False)
        ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
        ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

        ax1.set_xticks(list(severe_degree.keys())[:x_max], list(severe_degree.values())[:x_max])
        ax1.grid()
        ax1.set_axisbelow(True)
        ax2.grid()
        ax2.set_axisbelow(True)
        fig.savefig(f'./ratio_{age_cat}')




