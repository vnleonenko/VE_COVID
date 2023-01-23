import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

from visualization import plot_yll, plot_lost_gdp, plot_lost_profit


def calc_yll(dataframe):
    middle_ages = {0: 5, 1: 15, 2: 25, 3: 35, 4: 45, 5: 55, 6: 65, 7: 75, 8: 85, 9: 95}
    dataframe = dataframe.assign(middle_age=
                                [middle_ages[age_cat] for age_cat in dataframe['age_cat']])

    male_df = dataframe[dataframe['is_female'] == 0]
    male_df = male_df.assign(lost_years=69 - male_df['middle_age'])
    male_df = male_df[(male_df['age_cat'] <= 6) & (male_df['age_cat'] >= 2)]

    female_df = dataframe[dataframe['is_female'] == 1]
    female_df = female_df.assign(lost_years=78 - female_df['middle_age'])
    female_df = female_df[(female_df['age_cat'] <= 7) & (female_df['age_cat'] >= 2)]

    grouped_male_df = male_df.groupby(['age_cat'], as_index=False) \
        .agg({'lost_years': 'sum', 'size': lambda x: x.iloc[0]})
    grouped_male_df['crude_yll'] = grouped_male_df['lost_years'] / grouped_male_df['size'] * 1000

    grouped_female_df = female_df.groupby(['age_cat'], as_index=False) \
        .agg({'lost_years': 'sum', 'size': lambda x: x.iloc[0]})
    grouped_female_df['crude_yll'] = grouped_female_df['lost_years'] / grouped_female_df['size'] * 1000

    return grouped_male_df, grouped_female_df


def calc_lost_gdp_profit(dataframe, gdp, sample_size_m, sample_size_f):
    middle_ages = {0: 5, 1: 15, 2: 25, 3: 35, 4: 45, 5: 55, 6: 65, 7: 75, 8: 85, 9: 95}
    dataframe = dataframe.assign(middle_age=
                                [middle_ages[age_cat] for age_cat in dataframe['age_cat']])

    male_df = dataframe[dataframe['is_female'] == 0]
    male_df = male_df.assign(lost_years=61.5 - male_df['middle_age'])
    male_df = male_df[(male_df['age_cat'] <= 5) & (male_df['age_cat'] >= 2)]

    female_df = dataframe[dataframe['is_female'] == 1]
    female_df = female_df.assign(lost_years=56.5 - female_df['middle_age'])
    female_df = female_df[(female_df['age_cat'] <= 5) & (female_df['age_cat'] >= 2)]

    grouped_male_df = male_df.groupby(['age_cat'], as_index=False) \
        .agg({'lost_years': 'sum', 'size': lambda x: x.iloc[0]}).sum()
    grouped_male_df['lost_gdp_profit'] = grouped_male_df['lost_years'] * gdp / sample_size_m

    grouped_female_df = female_df.groupby(['age_cat'], as_index=False) \
        .agg({'lost_years': 'sum', 'size': lambda x: x.iloc[0]}).sum()
    grouped_female_df['lost_gdp_profit'] = grouped_female_df['lost_years'] * gdp / sample_size_f

    return grouped_male_df, grouped_female_df


if __name__ == '__main__':
    dest_folder = 'initial_data'
    folder_path = f'./{dest_folder}/'
    region_ids = pd.read_table(folder_path + 'region_id.tsv')
    vaccine_code = pd.read_table(folder_path + 'vaccine_code.tsv')
    severe_outcome = pd.read_table(folder_path + 'tyazh_outcome.dict.tsv')
    data = pd.read_table(folder_path + '202202_niig.tsv')
    fully_vac_ids = []
    inf_vac_ids = []
    with open('../unaggregated_data/input/fully_vac_ids.txt', 'r') as f:
        for line in f.readlines():
            fully_vac_ids.append(int(line.strip()))

    with open('../unaggregated_data/input/inf_vac_ids.txt', 'r') as f:
        for line in f.readlines():
            inf_vac_ids.append(int(line.strip()))

    inf_feb = data[(data['event_date'].str.contains('2022-02')) & (data['event_type'] == 'i')]
    tyazh_sample = inf_feb[inf_feb['tyazh_code'].isin([1, 2, 3])]

    severe_outcome = {1: 7, 2: 21, 3: 60}
    tyazh_sample = tyazh_sample.assign(lost_days=[severe_outcome[days_num]
                                                  for days_num in tyazh_sample['tyazh_code']])
    population1 = tyazh_sample.drop(tyazh_sample[tyazh_sample['id'].isin(fully_vac_ids + inf_vac_ids)].index)
    population2 = tyazh_sample[tyazh_sample['id'].isin(fully_vac_ids + inf_vac_ids)]

    lost_days_sum1 = population1.groupby(['age_cat', 'is_female'], as_index=False).agg({'lost_days': 'sum'})
    lost_days_sum2 = population2.groupby(['age_cat', 'is_female'], as_index=False).agg({'lost_days': 'sum'})

    lost_days_male1 = lost_days_sum1[(lost_days_sum1['is_female'] == 0) &
                                     lost_days_sum1['age_cat'].isin([2, 3, 4, 5])]
    lost_days_female1 = lost_days_sum1[(lost_days_sum1['is_female'] == 1) &
                                       lost_days_sum1['age_cat'].isin([2, 3, 4])]

    lost_days_male2 = lost_days_sum2[(lost_days_sum2['is_female'] == 0) &
                                     lost_days_sum2['age_cat'].isin([2, 3, 4, 5])]
    lost_days_female2 = lost_days_sum2[(lost_days_sum2['is_female'] == 1) &
                                       lost_days_sum2['age_cat'].isin([2, 3, 4])]

    # size of age group(?)
    '''inf_feb = data[data['event_date'].str.contains('2022-02')]
    male_sample_size = inf_feb[inf_feb['is_female'] == 0]['id'].unique().size
    female_sample_size = inf_feb[inf_feb['is_female'] == 1]['id'].unique().size'''


    male_sample_size1 = population1[population1['is_female'] == 0][['id', 'age_cat']]\
        .drop_duplicates('id', keep='first')\
        .groupby('age_cat', as_index=False).size()
    male_sample_size1 = male_sample_size1[male_sample_size1['age_cat'].isin([2, 3, 4, 5])]
    female_sample_size1 = population1[population1['is_female'] == 1][['id', 'age_cat']] \
        .drop_duplicates('id', keep='first') \
        .groupby('age_cat', as_index=False).size()
    female_sample_size1 = female_sample_size1[female_sample_size1['age_cat'].isin([2, 3, 4])]

    male_sample_size2 = population2[population2['is_female'] == 0][['id', 'age_cat']] \
        .drop_duplicates('id', keep='first') \
        .groupby('age_cat', as_index=False).size()
    male_sample_size2 = male_sample_size2[male_sample_size2['age_cat'].isin([2, 3, 4, 5])]
    female_sample_size2 = population2[population2['is_female'] == 1][['id', 'age_cat']] \
        .drop_duplicates('id', keep='first') \
        .groupby('age_cat', as_index=False).size()
    female_sample_size2 = female_sample_size2[female_sample_size2['age_cat'].isin([2, 3, 4])]

    gdp_2021 = 927540
    lost_days_male1['lost_gdp'] = lost_days_male1['lost_days'] / 365 * \
                                  gdp_2021 / male_sample_size1['size'].tolist()
    lost_days_female1['lost_gdp'] = lost_days_female1['lost_days'] / 365 * \
                                    gdp_2021 / female_sample_size1['size'].tolist()

    lost_days_male2['lost_gdp'] = lost_days_male2['lost_days'] / 365 * \
                                  gdp_2021 / male_sample_size2['size'].tolist()
    lost_days_female2['lost_gdp'] = lost_days_female2['lost_days'] / 365 * \
                                    gdp_2021 / female_sample_size2['size'].tolist()

    plot_lost_profit([lost_days_male1, lost_days_male2])
    plot_lost_profit([lost_days_female1, lost_days_female2], female_pop=True)
    '''

    # расчет экономического показателя для потерянных лет трудоспособной жизни
    gdp_2021 = 927540
    population1 = data[data['exclude_code'] == 1]
    age_cat_size = population1.drop_duplicates('id').groupby(['age_cat', 'is_female'], as_index=False).size()
    population1 = population1.merge(age_cat_size, on=['is_female', 'age_cat'], how='left')

    population2 = population1[population1['id'].isin(fully_vac_ids + inf_vac_ids)]
    vac_sample = data[data['id'].isin(fully_vac_ids + inf_vac_ids)]
    age_cat_vac_size = vac_sample.drop_duplicates('id').groupby(['age_cat', 'is_female'], as_index=False).size()
    population2 = population2.merge(age_cat_vac_size, on=['age_cat', 'is_female'],
                                    how='left', suffixes=('_pop1', ''))

    population3 = population1[~population1['id'].isin(fully_vac_ids + inf_vac_ids)]
    age_cat_size = population3.drop_duplicates('id').groupby(['age_cat', 'is_female'], as_index=False).size()
    population3 = population3.merge(age_cat_size, on=['is_female', 'age_cat'],
                                    how='left', suffixes=('_pop1', ''))

    # lost_gdp_male, lost_gdp_female = calc_lost_gdp_profit(population1, gdp_2021, male_sample_size, female_sample_size)
    lost_gdp_male2, lost_gdp_female2 = calc_lost_gdp_profit(population2, gdp_2021,
                                                            male_sample_size, female_sample_size)
    lost_gdp_male3, lost_gdp_female3 = calc_lost_gdp_profit(population3, gdp_2021,
                                                            male_sample_size, female_sample_size)

    gdp_pop1 = [lost_gdp_male3['lost_gdp_profit'], lost_gdp_female3['lost_gdp_profit']]
    gdp_pop2 = [lost_gdp_male2['lost_gdp_profit'], lost_gdp_female2['lost_gdp_profit']]
    plot_lost_gdp(gdp_pop1, gdp_pop2)

    '''
    pop1_male, pop1_female = calc_yll(population1)
    pop2_male, pop2_female = calc_yll(population2)

    pop1_female['vac_percentage'] = (pop2_female['size'] / pop1_female['size'] * 100).tolist()
    pop1_male['vac_percentage'] = (pop2_male['size'] / pop1_male['size'] * 100).tolist()

    plot_yll([pop1_male, pop2_male], pop1_male['vac_percentage'], output_folder='output/yll')
    plot_yll([pop1_male, pop2_male], pop1_male['vac_percentage'], female_pop=True,
             output_folder='output/yll')
