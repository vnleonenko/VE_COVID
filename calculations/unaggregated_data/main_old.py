import numpy as np
import pandas as pd
from utils_old import read_file
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils_old import count_healthy_sample, count_fully_vac_sample, get_inf_vac_ids, count_inf_vac_sample
from utils_old import plot_ratio_plt, get_fully_vaccinated_ids, add_period_from_last_record


if __name__ == "__main__":
    dest_folder = 'initial_data'
    folder_path = f'./{dest_folder}/'
    region_ids = read_file(folder_path + 'region_id.tsv')
    vaccine_code = read_file(folder_path + 'vaccine_code.tsv')
    severe_outcome = read_file(folder_path + 'tyazh_outcome.dict.tsv')
    data = read_file(folder_path + '202202_niig.tsv')

    # заболевшие в феврале
    inf_feb = data[(data['event_date'].str.contains('2022-02')) & (data['event_type'] == 'i')]

    # убираем заболевших в феврале
    data_wo_feb = pd.concat([data, inf_feb]).drop_duplicates(keep=False)
    data_wo_feb['tyazh_code'] = data_wo_feb['tyazh_code'].replace(np.nan, 0)

    fully_vac_ids = get_fully_vaccinated_ids(data_wo_feb)
    fully_vac_traj = data[data['id'].isin(fully_vac_ids)]

    # убираем заболевших в феврале
    inf_feb_mask = (fully_vac_traj['id'].isin(inf_feb['id'])) & (fully_vac_traj['event_type'] == 'i')
    fully_vac_traj = fully_vac_traj[~inf_feb_mask]

    # получаем последние записи полностью вакцинированных пациентов
    fully_vac = add_period_from_last_record(fully_vac_traj, inf_feb)

    # выбираем записи, которые внесены менее, чем 6 месяцев назад
    fully_vac_sample_6m = fully_vac[fully_vac['months_diff'] <= 6]
    fully_vac_sample = count_fully_vac_sample(inf_feb, fully_vac_sample_6m['id'].unique())

    # здоровые, которые заболели в феврале, и имеют 1 запись
    healthy_sample, healthy_sample_ids = count_healthy_sample(data)
    healthy_traj = data[data['id'].isin(healthy_sample_ids)]

    # убираем из датафрейма здоровых, полностью вакцинированных и заразившихся в феврале
    inf_vac_traj = data[~(data['id'].isin(healthy_sample_ids)) | (data['id'].isin(fully_vac_ids))]
    inf_vac_traj = inf_vac_traj[~((inf_vac_traj['id'].isin(inf_feb['id'])) &
                                  (inf_vac_traj['event_type'] == 'i'))]

    # добавляем столбец months_diff для сортировки по периоду, прошедшему с последней записи
    inf_vac_last_records = add_period_from_last_record(inf_vac_traj, inf_feb)
    # получаем словарь, где ключ - временные отрезки (6, 9, 12, 15), значения - id пациентов
    inf_vac_ids = get_inf_vac_ids(inf_vac_last_records)
    inf_vac_samples = {k: count_inf_vac_sample(inf_feb, v) for k, v in inf_vac_ids.items()}

    age_cats = [2, 6]
    subject_id = 78
    df_titles = {0: 'невакцинированные',
                 1: 'вакцинированные(до 6 месяцев)',
                 2: 'заболевшие и вакц.(до 6 месяцев)'}

    inf_vac_titles = {0: 'заболевшие и вакцинированные(до 6 месяцев)',
                      1: 'заболевшие и вакцинированные(от 6 до 9 месяцев)',
                      2: 'заболевшие и вакцинированные(от 9 до 12 месяцев)',
                      3: 'заболевшие и вакцинированные(от 12 до 15 месяцев)',
                      4: 'заболевшие и вакцинированные(более 15 месяцев)'}

    '''dfs = []
    for i in range(len(inf_vac_titles)):
        dfs.append(pd.read_csv(f'./zab_vac_df_{i}.csv'))'''

    dfs = [healthy_sample, fully_vac_sample, inf_vac_samples['<6']]
    # dfs = list(inf_vac_samples.values())
    plot_ratio_plt(dfs, subject_id, age_cats, region_ids, df_titles)
    # plot_ratio_plt(dfs, subject_id, age_cats, region_ids, inf_vac_titles)
