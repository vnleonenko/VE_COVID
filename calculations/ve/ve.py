import numpy as np
import pandas as pd
from tqdm import tqdm

from .utils import connect_to_db, query_to_df, add_aggregated_data, group_by_subjects
from .pcv_ppv import compute_ppv
import statsmodels.formula.api as smf
import statsmodels.api as sm


def compute_ve(pcv, ppv):
    ve_columns = ['data_point', 'region', 'vac_interval_group', 'vaccine',
                  've_zab_18_59', 've_hosp_18_59', 've_severe_18_59', 've_death_18_59',
                  've_zab_60', 've_hosp_60', 've_severe_60', 've_death_60',
                  've_zab_total', 've_hosp_total', 've_severe_total', 've_death_total']
    ve_df = pd.DataFrame(columns=ve_columns)
    merged_pcv_ppv = ppv.merge(pcv, on=['data_point', 'region', 'vac_interval_group', 'vaccine'],
                               how='outer')
    for ve_column in ve_columns:
        if ve_column in pcv.columns and ve_column in ppv.columns:
            ve_df[ve_column] = merged_pcv_ppv[ve_column]
        else:
            if '18_59' in ve_column:
                age = '_18_59'
            elif '60' in ve_column:
                age = '_60'
            else:
                age = '_total'
            case = ve_column.split('_')[1]
            factor_pcv = merged_pcv_ppv['pcv_' + case + age] / (1 - merged_pcv_ppv['pcv_' + case + age])
            factor_ppv = (1 - merged_pcv_ppv['ppv' + age]) / merged_pcv_ppv['ppv' + age]
            ve_df[ve_column] = round(1 - (factor_pcv * factor_ppv), 5)

    return ve_df


def compute_ve_conf_int(inf_vac_data, ppv_data):
    def interim_df(args):
        # print(args)
        case, vac_case, ppv = int(args[0]), int(args[1]), args[2]
        df = pd.DataFrame(columns=['case', 'vac_case', 'ppv'])
        df['y'] = [1 if i <= vac_case else 0 for i in range(case)]
        if ppv == 0:
            return np.nan, np.nan, np.nan

        df['logit_ppv'] = np.log(ppv / (1 - ppv))
        df = df.fillna({'case': case, 'vac_case': vac_case, 'ppv': ppv})
        glm = smf.glm(formula='y ~ 1', data=df, offset=df['logit_ppv'],
                      family=sm.families.Binomial()).fit()
        ve_estimation = round(1 - np.exp(glm.params).values[0], 5)
        ci = [round(ci, 5) for ci in 1 - np.exp(glm.conf_int(alpha=0.05)).values[0]]
        print(ve_estimation, *ci)
        return ve_estimation, ci[1], ci[0]

    merged_df = ppv_data.merge(inf_vac_data, on=['data_point', 'region', 'vac_interval_group', 'vaccine'], how='outer')
    # nans_sum1 = merged_df.isnull().sum().sum()
    merged_df.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

    merged_df.iloc[:, :4] = merged_df.iloc[:, :4].astype('category')
    merged_df.iloc[:, 4:7] = merged_df.iloc[:, 4:7].astype('float32')
    merged_df.iloc[:, 7:] = merged_df.iloc[:, 7:].astype('int32')

    merged_df_cut = merged_df.iloc[:100, :]

    ve_df = merged_df_cut[['data_point', 'region', 'vac_interval_group', 'vaccine']]
    case_age = ['zab_18_59', 'hosp_18_59', 'severe_18_59', 'death_18_59',
                'zab_60', 'hosp_60', 'severe_60', 'death_60',
                'zab_total', 'hosp_total', 'severe_total', 'death_total']

    for ca in tqdm(case_age):
        inf_column = 'count_' + ca
        inf_vac_column = 'count_vac_' + ca
        ppv_column = 'ppv_' + "_".join(ca.split('_')[1:])
        ve_column = 've_' + ca
        cil_column = 'cil_' + ca
        cih_column = 'cih_' + ca
        ve_df[[ve_column, cil_column, cih_column]] = \
            merged_df_cut[[inf_column, inf_vac_column, ppv_column]].apply(lambda x: interim_df(x) if np.all(x[:2]) != 0
        else [np.nan, np.nan, np.nan], axis=1, result_type="expand")

    ve_df.to_csv(f'calculations/output/ve_w_ci_test.csv', sep=';', index=False, encoding='cp1251', na_rep='NULL')
    return ve_df


def main():
    inf_vac_q = '''
    select sq3.*, 
        sq3.count_vac_zab_18_59 + sq3.count_vac_zab_60 as count_vac_zab_total,
        sq3.count_vac_hosp_18_59 + sq3.count_vac_hosp_60 as count_vac_hosp_total,
        sq3.count_vac_severe_18_59 + sq3.count_vac_severe_60 as count_vac_severe_total,
        sq3.count_vac_death_18_59 + sq3.count_vac_death_60 as count_vac_death_total
    from
            (select sq2.data_point, sq2.region, sq2.vac_interval_group, sq2.vaccine,
            sum(count_vac_zab_18_59) as count_vac_zab_18_59, sum(count_vac_hosp_18_59) as count_vac_hosp_18_59,
            sum(count_vac_severe_18_59) as count_vac_severe_18_59, sum(count_vac_death_18_59) as count_vac_death_18_59,
        
            sum(count_vac_zab_60) as count_vac_zab_60, sum(count_vac_hosp_60) as count_vac_hosp_60,
            sum(count_vac_severe_60) as count_vac_severe_60, sum(count_vac_death_60) as count_vac_death_60
        
            from 
            (select sq1.data_point, sq1.region, sq1.vac_interval_group, sq1.vaccine,
                case when sq1.age_group = '18-59' then sq1.count_vac_zab  else 0 end as count_vac_zab_18_59,
                case when sq1.age_group = '18-59' then sq1.count_vac_hosp  else 0 end as count_vac_hosp_18_59,
                case when sq1.age_group = '18-59' then sq1.count_vac_severe  else 0 end as count_vac_severe_18_59,
                case when sq1.age_group = '18-59' then sq1.count_vac_death  else 0 end as count_vac_death_18_59,
        
                case when sq1.age_group = '60+' then sq1.count_vac_zab  else 0 end as count_vac_zab_60,
                case when sq1.age_group = '60+' then sq1.count_vac_hosp  else 0 end as count_vac_hosp_60,
                case when sq1.age_group = '60+' then sq1.count_vac_severe  else 0 end as count_vac_severe_60,
                case when sq1.age_group = '60+' then sq1.count_vac_death  else 0 end as count_vac_death_60
            from 
                (select data_point, region, vac_interval_group, vaccine, age_group,
                        sum(count_vac_zab) as count_vac_zab, sum(count_vac_hosp) as count_vac_hosp,
                        sum(count_vac_severe) as count_vac_severe, sum(count_vac_death) as count_vac_death
                from dbo.ZAB_VAC_VIEW
                where data_point not like '%[B]%' and age_group <> '17-'
                group by data_point, region, vac_interval_group, vaccine, age_group
                ) as sq1
            ) as sq2
            group by sq2.data_point, sq2.region, sq2.vac_interval_group, sq2.vaccine
    ) as sq3
    order by sq3.data_point, sq3.region, sq3.vac_interval_group, sq3.vaccine
    '''
    inf_q = '''
    select sq3.*,
           sq3.count_zab_18_59 + sq3.count_zab_60 as count_zab_total,
           sq3.count_hosp_18_59 + sq3.count_hosp_60 as count_hosp_total,
           sq3.count_severe_18_59 + sq3.count_severe_60 as count_severe_total,
           sq3.count_death_18_59 + sq3.count_death_60 as count_death_total
    from
    (select sq2.data_point, sq2.region, 
            sum(sq2.count_zab_18_59) as count_zab_18_59,
            sum(sq2.count_hosp_18_59) as count_hosp_18_59,
            sum(sq2.count_severe_18_59) as count_severe_18_59,
            sum(sq2.count_death_18_59) as count_death_18_59,
    
            sum(sq2.count_zab_60) as count_zab_60,
            sum(sq2.count_hosp_60) as count_hosp_60,
            sum(sq2.count_severe_60) as count_severe_60,
            sum(sq2.count_death_60) as count_death_60
    
    from
    
        (select sq1.data_point, sq1.region,
                case when sq1.age_group = '18-59' then sq1.count_zab  else 0 end as count_zab_18_59,
                case when sq1.age_group = '18-59' then sq1.count_hosp  else 0 end as count_hosp_18_59,
                case when sq1.age_group = '18-59' then sq1.count_severe  else 0 end as count_severe_18_59,
                case when sq1.age_group = '18-59' then sq1.count_death  else 0 end as count_death_18_59,
    
                case when sq1.age_group = '60+' then sq1.count_zab  else 0 end as count_zab_60,
                case when sq1.age_group = '60+' then sq1.count_hosp  else 0 end as count_hosp_60,
                case when sq1.age_group = '60+' then sq1.count_severe  else 0 end as count_severe_60,
                case when sq1.age_group = '60+' then sq1.count_death  else 0 end as count_death_60
    
        from
        
            --аггрегация таблицы заразившихся с исключением разбивки по половому признаку
            (select data_point, region, age_group, 
                    sum(count_zab) as count_zab, sum(count_hosp) as count_hosp, 
                    sum(count_severe) as count_severe, sum(count_death) as count_death
            from dbo.ZAB_VIEW
            where data_point not like '%[B]%' and age_group <> '17-'
            group by data_point, region, age_group) as sq1
        ) as sq2
        group by sq2.data_point, sq2.region) as sq3
    order by sq3.data_point, sq3.region
    '''
    vac_q = '''
    select sq3.*, sq3.vac_count_18_59 + sq3.vac_count_60 as vac_count_total
	from
		(select sq2.data_point, sq2.region, sq2.vac_interval_group, sq2.vaccine,
		sum(sq2.vac_count_18_59) as vac_count_18_59,
		sum(sq2.vac_count_60) as vac_count_60
		from 
			(select sq1.data_point, sq1.region, sq1.vac_interval_group, sq1.vaccine,
			case when sq1.age_group = '18-59' then sq1.vac_count else 0 end as vac_count_18_59,
			case when sq1.age_group = '60+' then sq1.vac_count else 0 end as vac_count_60
			from
				(select  data_point, region, vac_interval_group, vaccine,
				age_group, sum(vac_count) as vac_count
				from dbo.VAC_VIEW
				where data_point not like '%[B]%' and age_group <> '17-'
				group by data_point, region, vac_interval_group, vaccine, age_group
				) as sq1
			) as sq2
			group by sq2.data_point, sq2.region, sq2.vac_interval_group, sq2.vaccine
		) as sq3	
    order by sq3.data_point, sq3.region, sq3.vac_interval_group'''
    pop_q = '''select region, nas_age_18_59_total, nas_age_60_total, nas_age_adult_total 
        		from dbo.NAS_AGE'''

    inf_vac_columns = ['data_point', 'region', 'vac_interval_group', 'vaccine',
                       'count_vac_zab_18_59', 'count_vac_hosp_18_59', 'count_vac_severe_18_59', 'count_vac_death_18_59',
                       'count_vac_zab_60', 'count_vac_hosp_60', 'count_vac_severe_60', 'count_vac_death_60',
                       'count_vac_zab_total', 'count_vac_hosp_total', 'count_vac_severe_total', 'count_vac_death_total']
    inf_columns = ['data_point', 'region',
                   'count_zab_18_59', 'count_hosp_18_59', 'count_severe_18_59', 'count_death_18_59',
                   'count_zab_60', 'count_hosp_60', 'count_severe_60', 'count_death_60',
                   'count_zab_total', 'count_hosp_total', 'count_severe_total', 'count_death_total']
    vac_columns = ['data_point', 'region', 'vac_interval_group', 'vaccine',
                   'vac_count_18_59', 'vac_count_60', 'vac_count_total']
    pop_columns = ['region', 'nas_age_18_59', 'nas_age_60', 'nas_age_adult_total']

    db_cursor = connect_to_db()

    inf_vac_df = query_to_df(inf_vac_q, db_cursor, inf_vac_columns)
    inf_df = query_to_df(inf_q, db_cursor, inf_columns)
    vac_df = query_to_df(vac_q, db_cursor, vac_columns)
    pop_df = query_to_df(pop_q, db_cursor, pop_columns)

    inf_vac_grouped_df = add_aggregated_data(inf_vac_df, ['data_point', 'vac_interval_group', 'vaccine'],
                                             ['data_point', 'region', 'vac_interval_group'])
    inf_grouped_df = group_by_subjects(inf_df, ['data_point'])
    inf_grouped_df = pd.concat([inf_df, inf_grouped_df])
    inf_grouped_df.sort_values(by=['data_point', 'region'], inplace=True)
    inf_grouped_df.reset_index(inplace=True, drop=True)

    inf_vac_grouped_df = inf_vac_grouped_df.merge(inf_grouped_df, on=['data_point', 'region'],
                                                  how='left')

    vac_grouped_df = add_aggregated_data(vac_df, ['data_point', 'vac_interval_group', 'vaccine'],
                                         ['data_point', 'region', 'vac_interval_group'])
    vac_pop_grouped_df = vac_grouped_df.merge(pop_df, on='region', how='left')
    ppv_df = compute_ppv(vac_pop_grouped_df)
    '''
    vac_pop_grouped_df.to_csv('calculations/output/vac_pop.csv', sep=';', index=False, encoding='cp1251', na_rep='NULL')
    inf_vac_grouped_df.to_csv('calculations/output/inf_vac.csv', sep=';', index=False, encoding='cp1251', na_rep='NULL')
    ppv_df.to_csv('calculations/output/ppv.csv', sep=';', index=False, encoding='cp1251', na_rep='NULL')
    inf_vac_grouped_cut_df.to_csv('calculations/output/inf_vac_cut.csv', sep=';', index=False, encoding='cp1251',
                                  na_rep='NULL')
    '''

    # pcv_df = compute_pcv(inf_vac_grouped_df)
    # ve = compute_ve(pcv_df, ppv_df)

    inf_vac_grouped_cut_df = inf_vac_grouped_df.loc[inf_vac_grouped_df['data_point'] == '2022.07_16-08-2022']
    ppv_cut_df = ppv_df.loc[ppv_df['data_point'] == '2022.07_16-08-2022']  # '2021.11_01-07-2022'

    ve_conf_int = compute_ve_conf_int(inf_vac_grouped_cut_df, ppv_cut_df)
    ve_conf_int.to_csv('calculations/output/ve_w_ci.csv', sep=';', index=False, encoding='cp1251', na_rep='NULL')


if __name__ == '__main__':
    main()
