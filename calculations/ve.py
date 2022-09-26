import pandas as pd
from utils import connect_to_db, query_to_df, add_aggregated_data, group_by_subjects
from pcv_ppv import compute_ppv, compute_pcv


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
            factor_pcv = merged_pcv_ppv['pcv_'+case+age] / (1 - merged_pcv_ppv['pcv_'+case+age])
            factor_ppv = (1 - merged_pcv_ppv['ppv'+age]) / merged_pcv_ppv['ppv'+age]
            ve_df[ve_column] = 1 - (factor_pcv * factor_ppv)

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

    pcv_df = compute_pcv(inf_vac_grouped_df)
    ppv_df = compute_ppv(vac_pop_grouped_df)

    ve = compute_ve(pcv_df, ppv_df)
    ve.to_csv('calculations/output/ve.csv', sep=';', index=False, encoding='cp1251')


if __name__ == '__main__':
    main()




