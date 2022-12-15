import zipfile
import pandas as pd
import numpy as np


def unzip_archive(zip_path, dest_folder):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(f'./{dest_folder}', pwd=b'y6w09W8')


def read_file(file_path):
    return pd.read_table(file_path)


def count_total_infected(dataframe, group_by_regions=True, group_by_days=True):

    grouped_age_region = dataframe.groupby(['event_date', 'age_cat', 'region_id', 'tyazh_code']).size()
    grouped_age_region = grouped_age_region.rename('count')
    grouped_age_region = grouped_age_region.reset_index()
    grouped_age_region.sort_values(by=['event_date', 'age_cat', 'region_id', 'tyazh_code'], inplace=True)

    bare_columns = ['age_cat']
    if group_by_regions:
        bare_columns.append('region_id')
        region_agg_fn = lambda x:'РФ'
    else:
        region_agg_fn = lambda x: x.iloc[0]

    if group_by_days:
        bare_columns.append('event_date')
        event_date_agg_fn = lambda x: '2022-02'

    else:
        event_date_agg_fn = lambda x: x.iloc[0]
    group_by_columns = list(set(grouped_age_region.columns) - set(bare_columns))
    group_by_columns.remove('count')
    df = grouped_age_region.groupby(group_by_columns).agg({'event_date': event_date_agg_fn,
                                                           'region_id': region_agg_fn,
                                                           'tyazh_code': lambda x: x.iloc[0],
                                                           'count': 'sum'})
    df.reset_index(inplace=True, drop=True)
    return df


def get_vaccinated_sample(dataframe):
    vac_trajectories = dataframe[dataframe['tyazh_code'] == -1]
    grouped_trajectories = vac_trajectories.groupby(
        ['id', 'event_type', 'age_cat', 'region_id', 'vaccine_code']).agg(
        {'id': lambda x: x.iloc[0], 'event_type': lambda x: list(x),
         'age_cat': lambda x: x.iloc[0], 'region_id': lambda x: x.iloc[0],
         'vaccine_code': lambda x: list(x), 'stage_number': lambda x: list(x)})
    return grouped_trajectories


if __name__ == "__main__":
    # zip_path = 'niig_12122022.zip'
    dest_folder = 'data'
    # unzip_archive(zip_path, dest_folder)

    folder_path = f'./{dest_folder}/niig_12122022/'
    region_ids = read_file(folder_path + 'region_id.tsv')
    vaccine_code = read_file(folder_path + 'vaccine_code.tsv')
    severe_outcome = read_file(folder_path + 'tyazh_outcome.dict.tsv')
    data = read_file(folder_path + '202202_niig.tsv')

    inf_feb = data[(data['event_date'].str.contains('2022-02')) & (data['event_type'] != 'v')]
    total_inf_feb = count_total_infected(inf_feb, group_by_regions=False, group_by_days=True)
    total_inf_feb_spb = total_inf_feb[total_inf_feb['region_id'] == 78]

    # concat работает дольше для исключения заболевших в феврале
    #trajectories = pd.concat([data, inf_feb]).drop_duplicates(keep=False)
    combined = data.append(total_inf_feb)
    trajectories = combined[~combined.index.duplicated(keep=False)]

    # агрегирую данные, чтобы посчитать людей с количеством полученных вакцин == 2 в списках столбца 'stage_number' и
    # где значения должны быть [1, 2]
    trajectories = trajectories[(trajectories['region_id'] == 78)]
    trajectories['tyazh_code'].replace(np.nan, -1, inplace=True)
    vac_trajectories = get_vaccinated_sample(trajectories)


