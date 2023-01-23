import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

from utils import count_sample_size
from utils import get_inf_vac_ids, get_fully_vaccinated_ids, get_healthy_ids, get_revaccinated_ids
from utils import add_period_from_last_record, get_sample_by_vaccine

from yll import calc_yll

from visualization import plot_ratio, plot_yll


if __name__ == "__main__":
    dest_folder = 'initial_data'
    folder_path = f'./{dest_folder}/'
    region_ids = pd.read_table(folder_path + 'region_id.tsv')
    vaccine_code = pd.read_table(folder_path + 'vaccine_code.tsv')
    severe_outcome = pd.read_table(folder_path + 'tyazh_outcome.dict.tsv')
    data = pd.read_table(folder_path + '202202_niig.tsv')
    data['tyazh_code'] = data['tyazh_code'].replace(np.nan, 0)

    # заболевшие в феврале
    inf_feb = data[(data['event_date'].str.contains('2022-02')) & (data['event_type'] == 'i')]
    inf_feb = inf_feb.drop_duplicates('id', keep='last')
    inf_feb_sample = count_sample_size(inf_feb, inf_feb['id'].tolist())

    '''revac_ids = get_revaccinated_ids(data)
    revac_traj = data[data['id'].isin(revac_ids)]
    revac_traj = revac_traj.drop(revac_traj.drop_duplicates('id', keep='last').index)
    revac = add_period_from_last_record(revac_traj, inf_feb)
    revac_sample_6m = revac[revac['months_diff'] <= 6]
    revac_sample = count_sample_size(inf_feb, revac_sample_6m['id'].unique())'''

    fully_vac_ids = get_fully_vaccinated_ids(data)
    """with open('fully_vac_ids.txt', 'a') as f:
        for id in fully_vac_ids:
            f.write(str(id)+'\n')"""
    fully_vac_traj = data[data['id'].isin(fully_vac_ids)]

    # убираем заболевших в феврале
    fully_vac_traj = fully_vac_traj.drop(fully_vac_traj.drop_duplicates('id', keep='last').index)

    # получаем последние записи полностью вакцинированных пациентов
    fully_vac = add_period_from_last_record(fully_vac_traj, inf_feb)

    # выбираем записи, которые внесены менее, чем 6 месяцев назад
    fully_vac_sample_6m = fully_vac[fully_vac['months_diff'] <= 6]
    fully_vac_sample = count_sample_size(inf_feb, fully_vac_sample_6m['id'].unique())

    # здоровые, которые заболели в феврале, и имеют 1 запись
    healthy_sample_ids = get_healthy_ids(data)
    healthy_sample = count_sample_size(inf_feb, healthy_sample_ids)

    # убираем из датафрейма здоровых, полностью вакцинированных и заразившихся в феврале
    inf_vac_traj = data[~(data['id'].isin(healthy_sample_ids) | data['id'].isin(fully_vac_ids))]
    inf_vac_traj = inf_vac_traj.drop(inf_vac_traj.drop_duplicates('id', keep='last').index)

    # добавляем столбец months_diff для сортировки по периоду, прошедшему с последней записи
    inf_vac_last_records = add_period_from_last_record(inf_vac_traj, inf_feb)
    # получаем словарь, где ключ - временные отрезки ('<6', '6-9', '9-12', '12-15', '>=15'), значения - id пациентов
    inf_vac_ids = get_inf_vac_ids(inf_vac_last_records)
    inf_vac_samples = {k: count_sample_size(inf_feb, v) for k, v in inf_vac_ids.items()}
    '''inf_vac_sample_new = inf_vac_samples['<6'][inf_vac_samples['<6']['age_cat'].isin([6, 7, 8])]
    inf_vac_agg_ids = inf_vac_samples[inf_vac_samples['<6']['age_cat'] <= 5]['id']
    inf_vac_agg_age = count_sample(inf_feb, inf_vac_agg_ids)
    inf_vac_sample_new = pd.concat([inf_vac_agg_age[inf_vac_agg_age['age_cat'] == 'all'], inf_vac_sample_new])'''

    ages_dict = {2: '20-29 лет', 3: '30-39 лет', 4: '40-49 лет',  5: '50-59 лет',
                 6: '60-69 лет', 7: '70-79 лет', 8: '80 лет и больше'}
    age_groups_agg = {2: '20-29', 3: '30-39', 4: '40-49', 5: '50-59',  6: '60-69', 7: '70-79', 8: '80+'}
    subject = {99: 'РФ'}

    dfs = [healthy_sample, fully_vac_sample, inf_vac_samples['<6']]
    three_group_labels = {0: 'Невакцинированные и ранее неболевшие',
                          1: 'Вакцинированные',
                          2: 'Вакцинированные и переболевшие'}

    '''
    dfs = []
    for i in range(len(inf_vac_titles)):
        dfs.append(pd.read_csv(f'./zab_vac_df_{i}.csv'))
        
    inf_vac_titles = {0: 'заболевшие и вакцинированные(до 6 месяцев)',
                      1: 'заболевшие и вакцинированные(от 6 до 9 месяцев)',
                      2: 'заболевшие и вакцинированные(от 9 до 12 месяцев)',
                      3: 'заболевшие и вакцинированные(от 12 до 15 месяцев)',
                      4: 'заболевшие и вакцинированные(более 15 месяцев)'}
    plot_ratio(dfs, subject_id, age_groups, region_ids, inf_vac_titles) 
    '''

    two_group_labels = {0: 'Все население',
                        1: 'Вакцинированное население (ПВН 100%)'}
    vac_sample = count_sample_size(inf_feb, fully_vac_sample_6m['id'].tolist()+inf_vac_ids['<6'])
    inf_feb_size = inf_feb_sample[inf_feb_sample['region_id'] == 99].groupby(['age_cat'], as_index=False)\
        .agg({'size_total': lambda x: x.iloc[0]})
    vac_size = vac_sample[vac_sample['region_id'] == 99].groupby(['age_cat'], as_index=False)\
        .agg({'size_total': lambda x: x.iloc[0]})

    inf_feb_size['vac_percentage'] = vac_size['size_total'] / inf_feb_size['size_total'] * 100
    vac_percentage = inf_feb_size[inf_feb_size['age_cat'].isin(list(range(2, 9)))]['vac_percentage']
    '''plot_ratio([inf_feb_sample, vac_sample], subject, ages_dict, two_group_labels,
               vac_percentage.tolist(), 'output/all_vac')
    
    plot_ratio(dfs, subject, ages_dict, three_group_labels, output_folder='output/healthy_vac_inf_vac')
    plot_ratio([inf_feb_sample, vac_sample, revac], subject, ages_dict,
               {0: 'Все население',
                1: 'Вакцинированное население (ПВН 100%)',
                2: 'Ревакцинированное население'}, output_folder='output/all_vac_revac')'''

    fully_vac_sputnik_sample, revac_sputnik_sample = get_sample_by_vaccine(data, fully_vac_traj, inf_feb,
                                                                           vaccine_code=1)
    '''plot_ratio([inf_feb_sample, fully_vac_sputnik_sample, revac_sputnik_sample], subject, ages_dict,
               {0: ('Все население', 'tab:blue'),
                1: ('Население вакцинированное Спутником V', 'tab:green'),
                2: ('Население peвакцинированное Спутником V/Лайт', 'tab:orange')},
               vac_percentage.tolist(), 'output/all_vac_revac_sputnik')'''

    fully_vac_covivac_sample, revac_covivac_sample = get_sample_by_vaccine(data, fully_vac_traj, inf_feb,
                                                                           vaccine_code=4)
    '''plot_ratio([inf_feb_sample, fully_vac_covivac_sample, revac_covivac_sample], subject, ages_dict,
               {0: ('Все население', 'tab:blue'),
                1: ('Население вакцинированное КовиВаком', 'tab:orange'),
                2: ('Население peвакцинированное Спутником V/Лайт', 'tab:green')},
               vac_percentage.tolist(), 'output/all_vac_revac_covivac')'''
    not_vac_ids = data[~data['id'].isin(data[data['event_type'] == 'v']['id'])]['id']
    not_vac_ids_wo_healthy = not_vac_ids[~not_vac_ids.isin(healthy_sample_ids.tolist())]
    not_vac_sample = count_sample_size(inf_feb, not_vac_ids_wo_healthy)

    plot_ratio([revac_covivac_sample, not_vac_sample, revac_sputnik_sample], {99: 'РФ'}, ages_dict,
               {0: ('Вакц. КовиВаком и ревакц. Спутником V/Лайт', 'tab:orange'),
                1: ('Невакцинированные переболевшие', 'tab:blue'),
                2: ('Вакц. Спутником V и ревакц. Спутником V/Лайт', 'tab:green')}, output_folder='output')

    plot_ratio([inf_feb_sample, revac_covivac_sample, revac_sputnik_sample], {99: 'РФ'}, ages_dict,
               {0: ('Все население', 'tab:blue'),
                1: ('Вакц. КовиВаком и ревакц. Спутником V/Лайт', 'tab:orange'),
                2: ('Вакц. Спутником V и ревакц. Спутником V/Лайт', 'tab:green')},
               vac_percentage.tolist(), 'output')
