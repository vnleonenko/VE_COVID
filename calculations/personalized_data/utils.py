import zipfile
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import locale
from matplotlib.ticker import MaxNLocator


def unzip_archive(zip_path, dest_folder):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(f'./{dest_folder}', pwd=b'y6w09W8')


def get_healthy_ids(dataframe):
    grouped_data = dataframe.groupby('id', as_index=False).size()
    ids = grouped_data[grouped_data['size'] == 1]['id']
    sample = dataframe[dataframe['id'].isin(ids.tolist())]
    healthy_sample_ids = sample.loc[sample['event_type'] == 'i', 'id']

    return healthy_sample_ids


def get_fully_vaccinated_ids(dataframe):
    inf_vac_trajectories = dataframe.drop(dataframe.drop_duplicates('id', keep='last').index)
    inf_vac_size = inf_vac_trajectories.groupby(['id', 'event_type'], as_index=False).size()
    # убираем id пациентов, которые и болели, и вакцинировались, убирая повторяющиеся id
    # с разным типом событий для них в выборке
    only_vac_ids = inf_vac_size.drop_duplicates('id', keep=False)['id']

    return only_vac_ids


def get_revaccinated_ids(dataframe):
    inf_vac_trajectories = dataframe.drop(dataframe.drop_duplicates('id', keep='last').index)
    inf_vac_size = inf_vac_trajectories.groupby(['id', 'event_type'], as_index=False).size()
    revac_size = inf_vac_size[inf_vac_size['size'] > 2]
    revac_ids = revac_size['id'].unique()
    return revac_ids


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
            res_dict.update({f'{str(left_bound)}-{str(right_bound)}': ids.tolist()})
            ids = dataframe[(dataframe['months_diff'] >= right_bound)]['id']
            res_dict.update({f'>={str(right_bound)}': ids.tolist()})
        else:
            left_bound = last_event_int[i - 1]
            ids = dataframe[(dataframe['months_diff'] >= left_bound) &
                            (dataframe['months_diff'] < right_bound)]['id']
            res_dict.update({f'{str(left_bound)}-{str(right_bound)}': ids.tolist()})
    return res_dict


def count_sample_size(inf_df, ids):
    inf_df_corr = inf_df[(inf_df['age_cat'] != 0) &
                    (inf_df['age_cat'] != 1) &
                    (inf_df['tyazh_code'] != 0)]
    inf_df_corr.loc[inf_df_corr['age_cat'] == 9, 'age_cat'] = 8
    inf_df_corr = inf_df_corr.drop(inf_df_corr[inf_df_corr['region_id'] == 99].index)

    if len(ids) == inf_df.shape[0]:
        feb_sample = inf_df_corr.drop_duplicates('id')
    else:
        feb_sample = inf_df_corr[inf_df_corr['id'].isin(ids)]
        feb_sample = feb_sample.drop_duplicates('id')

    sample_tyazh_size = feb_sample.groupby(['region_id', 'age_cat', 'tyazh_code'], as_index=False).size()
    '''grouped_by_age = sample_tyazh_size.groupby(['region_id', 'tyazh_code'],
                                    as_index=False).agg({'region_id': lambda x: x.iloc[0],
                                                         'age_cat': lambda x: 'all',
                                                         'size': 'sum'})'''
    grouped_by_region = sample_tyazh_size.groupby(['age_cat', 'tyazh_code'], as_index=False)\
        .agg({'region_id': lambda x: 99, 'size': 'sum'})
    sample_tyazh_size = pd.concat([sample_tyazh_size, grouped_by_region])  # grouped_by_age

    sample_total_size = feb_sample.groupby(['region_id', 'age_cat'], as_index=False).size()  # .agg({'size': 'sum'})
    '''grouped_by_age_total = sample_total_size.groupby(['region_id'], as_index=False)\
        .agg({'region_id': lambda x: x.iloc[0], 'age_cat': lambda x: 'all', 'size': 'sum'})'''
    grouped_by_region_total = sample_total_size.groupby(['age_cat'], as_index=False) \
        .agg({'region_id': lambda x: 99, 'size': 'sum'})
    sample_total_size = pd.concat([sample_total_size, grouped_by_region_total])  # grouped_by_age_total

    res_sample = sample_tyazh_size.merge(sample_total_size, on=['region_id', 'age_cat'], how='left',
                                         suffixes=('_tyazh', '_total'))
    res_sample['ratio'] = res_sample['size_tyazh'] / res_sample['size_total']
    return res_sample


def add_period_from_last_record(df, inf_feb):
    last_records = df.drop_duplicates('id', keep='last')
    last_records = last_records.merge(inf_feb[['id', 'event_date', 'event_type']],
                                      on='id', how='inner', suffixes=('_lr', '_feb'))
    last_records['event_date_lr'] = pd.to_datetime(last_records['event_date_lr'], errors='coerce', format='%Y-%m-%d')
    last_records['event_date_feb'] = pd.to_datetime(last_records['event_date_feb'], errors='coerce', format='%Y-%m-%d')
    infection_date = last_records['event_date_feb'].dt.date
    last_vac_date = last_records['event_date_lr'].dt.date

    last_records['months_diff'] = (infection_date - last_vac_date) / np.timedelta64(1, 'M')
    return last_records


def get_sample_by_vaccine(df, vac_df, inf_df, vaccine_code):
    vaccine_ids = [1, 2, 3, 4, 5, 7, 8]
    vac_w_vac_code = vac_df.groupby(['id', 'age_cat', 'vaccine_code'], as_index=False).size()
    one_record_vac = vac_w_vac_code.drop_duplicates('id', keep=False)
    fully_vac_ids = one_record_vac[(one_record_vac['vaccine_code'] == vaccine_code) &
                                   (one_record_vac['size'] == 2)]['id']
    revac_w_vac_code = vac_w_vac_code[
        ~vac_w_vac_code['id'].isin(one_record_vac.drop(one_record_vac[one_record_vac['size'] > 2].index)['id'])]

    revac_one_record = one_record_vac[(one_record_vac['size'] > 2) &
                                      (one_record_vac['vaccine_code'] == vaccine_code)]

    dupl_first_record = revac_w_vac_code.drop_duplicates('id', keep='first')
    not_target_vaccines = [vac_id for vac_id in vaccine_ids if vac_id != vaccine_code]
    revac_first_rec_ids = dupl_first_record.drop(
        dupl_first_record[dupl_first_record['vaccine_code'].isin(not_target_vaccines) |
                          (dupl_first_record['size'] == 1)].index)['id']
    revac_second_recs = revac_w_vac_code[revac_w_vac_code['id'].isin(revac_first_rec_ids)] \
        .drop_duplicates('id', keep='last')
    revac_second_rec_ids = revac_second_recs[revac_second_recs['vaccine_code'].isin([1, 5])]['id']
    revac_ids = pd.merge(revac_first_rec_ids, revac_second_rec_ids)['id']
    revac_ids = sorted(revac_ids.tolist() + revac_one_record['id'].tolist())

    fully_vac_traj = df[df['id'].isin(fully_vac_ids)]
    fully_vac_traj = fully_vac_traj.drop(
        fully_vac_traj.drop_duplicates('id', keep='last').index)
    fully_vac = add_period_from_last_record(fully_vac_traj, inf_df)
    fully_vac_6m = fully_vac[fully_vac['months_diff'] <= 6]
    fully_vac_sample = count_sample_size(inf_df, fully_vac_6m['id'].unique())

    revac_traj = df[df['id'].isin(revac_ids)]
    revac_traj = revac_traj.drop(revac_traj.drop_duplicates('id', keep='last').index)
    revac = add_period_from_last_record(revac_traj, inf_df)
    revac_6m = revac[revac['months_diff'] <= 6]
    revac_sample = count_sample_size(inf_df, revac_6m['id'].unique())
    return fully_vac_sample, revac_sample




