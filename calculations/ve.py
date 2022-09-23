import pandas as pd
from utils import connect_to_db, query_to_df, add_aggregated_data
from pcv_ppv import compute_ppv, compute_pcv


def compute_ve(pcv, ppv):
    ve_columns = ['data_point', 'region', 'vac_interval_group', 'vaccine',
                  've_zab_18_59', 've_hosp_18_59', 've_severe_18_59', 've_death_18_59',
                  've_zab_60', 've_hosp_60', 've_severe_60', 've_death_60',
                  've_zab_total', 've_hosp_total', 've_severe_total', 've_death_total']
    ve_df = pd.DataFrame(columns=ve_columns)
    for ve_column in ve_columns:
        if ve_column in pcv.columns and ve_column in ppv.columns:
            ve_df[ve_column] = pcv[ve_column]
        else:
            if '18_59' in ve_column:
                age = '_18_59'
            elif '60' in ve_column:
                age = '_60'
            else:
                age = '_total'
            case = ve_column.split('_')[1]
            factor_pcv = pcv['pcv_'+case+age] / (1 - pcv['pcv_'+case+age])
            factor_ppv = (1 - ppv['ppv'+age]) / ppv['ppv'+age]
            ve_df[ve_column] = 1 - factor_pcv * factor_ppv

    return ve_df


def main():
    inf_vac_q = '''
    set arithabort off;
    set ansi_warnings off;


    select *, 
    sq2.count_vac_zab_18_59 + sq2.count_vac_zab_60 as count_vac_zab_total,
    sq2.count_vac_hosp_18_59 + sq2.count_vac_hosp_60 as count_vac_hosp_total,
    sq2.count_vac_severe_18_59 + sq2.count_vac_severe_60 as count_vac_severe_total,
    sq2.count_vac_death_18_59 + sq2.count_vac_death_60 as count_vac_death_total,


    sq2.count_zab_18_59 + sq2.count_zab_60 as count_zab_total,
    sq2.count_hosp_18_59 + sq2.count_hosp_60 as count_hosp_total,
    sq2.count_severe_18_59 + sq2.count_severe_60 as count_severe_total,
    sq2.count_death_18_59 + sq2.count_death_60 as count_death_total

    from
    --объединение двух аггрегированных таблиц для вычисления pcv, доли заболевших среди вакцинированных
    	(select sq1.data_point, sq1.region, sq1.vac_interval_group, sq1.vaccine,
    	sum(count_vac_zab_18_59) as count_vac_zab_18_59,
    	sum(count_vac_hosp_18_59) as count_vac_hosp_18_59,
    	sum(count_vac_severe_18_59) as count_vac_severe_18_59,
    	sum(count_vac_death_18_59) as count_vac_death_18_59,

    	sum(count_vac_zab_60) as count_vac_zab_60,
    	sum(count_vac_hosp_60) as count_vac_hosp_60,
    	sum(count_vac_severe_60) as count_vac_severe_60,
    	sum(count_vac_death_60) as count_vac_death_60,

    	sum(count_zab_18_59) as count_zab_18_59,
    	sum(count_hosp_18_59) as count_hosp_18_59,
    	sum(count_severe_18_59) as count_severe_18_59,
    	sum(count_death_18_59) as count_death_18_59,

    	sum(count_zab_60) as count_zab_60,
    	sum(count_hosp_60) as count_hosp_60,
    	sum(count_severe_60) as count_severe_60,
    	sum(count_death_60) as count_death_60

    	from

    	(select left_t.data_point, left_t.region, left_t.vac_interval_group, left_t.vaccine,
    	case when left_t.age_group = '18-59' then left_t.count_vac_zab  else 0 end as count_vac_zab_18_59,
    	case when left_t.age_group = '18-59' then left_t.count_vac_hosp  else 0 end as count_vac_hosp_18_59,
    	case when left_t.age_group = '18-59' then left_t.count_vac_severe  else 0 end as count_vac_severe_18_59,
    	case when left_t.age_group = '18-59' then left_t.count_vac_death  else 0 end as count_vac_death_18_59,

    	case when left_t.age_group = '60+' then left_t.count_vac_zab  else 0 end as count_vac_zab_60,
    	case when left_t.age_group = '60+' then left_t.count_vac_hosp  else 0 end as count_vac_hosp_60,
    	case when left_t.age_group = '60+' then left_t.count_vac_severe  else 0 end as count_vac_severe_60,
    	case when left_t.age_group = '60+' then left_t.count_vac_death  else 0 end as count_vac_death_60,

    	case when left_t.age_group = '18-59' then right_t.count_zab  else 0 end as count_zab_18_59,
    	case when left_t.age_group = '18-59' then right_t.count_hosp  else 0 end as count_hosp_18_59,
    	case when left_t.age_group = '18-59' then right_t.count_severe  else 0 end as count_severe_18_59,
    	case when left_t.age_group = '18-59' then right_t.count_death  else 0 end as count_death_18_59,

    	case when left_t.age_group = '60+' then right_t.count_zab  else 0 end as count_zab_60,
    	case when left_t.age_group = '60+' then right_t.count_hosp  else 0 end as count_hosp_60,
    	case when left_t.age_group = '60+' then right_t.count_severe  else 0 end as count_severe_60,
    	case when left_t.age_group = '60+' then right_t.count_death  else 0 end as count_death_60


    	from
    		--аггрегация таблицы заразившихся среди вакцинированных с исключением разбивки по половому признаку
    		(select data_point, region, vac_interval_group, vaccine, age_group,
    				sum(count_vac_zab) as count_vac_zab, sum(count_vac_hosp) as count_vac_hosp,
    				sum(count_vac_severe) as count_vac_severe, sum(count_vac_death) as count_vac_death
    		from dbo.ZAB_VAC_VIEW
    		where data_point not like '%[B]%' and age_group <> '17-'
    		group by data_point, region, vac_interval_group, vaccine, age_group) as left_t
    	left join
    		--аггрегация таблицы заразившихся с исключением разбивки по половому признаку
    		(select data_point, region, age_group,
    				sum(count_zab) as count_zab, sum(count_hosp) as count_hosp, 
    				sum(count_severe) as count_severe, sum(count_death) as count_death
    		from dbo.ZAB_VIEW
    		where data_point not like '%[B]%' and age_group <> '17-'
    		group by data_point, region, age_group) as right_t

    	on (left_t.data_point = right_t.data_point) and (left_t.region = right_t.region) and (left_t.age_group = right_t.age_group)
    	)as sq1
    	group by sq1.data_point, sq1.region, sq1.vac_interval_group, sq1.vaccine
    ) as sq2
    order by sq2.data_point, sq2.region, sq2.vac_interval_group, sq2.vaccine
    '''
    vac_pop_q = '''
    select left_t.data_point, left_t.region, left_t.vac_interval_group, left_t.vaccine,
    left_t.vac_count_18_59, left_t.vac_count_60, left_t.vac_count_total,
    right_t.nas_age_18_59_total, right_t.nas_age_60_total, right_t.nas_age_adult_total

    from
    	(select *, sq3.vac_count_18_59 + sq3.vac_count_60 as vac_count_total
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
    	) as left_t
    	left join 
    		(select region, nas_age_18_59_total, nas_age_60_total, nas_age_adult_total 
    		from dbo.NAS_AGE) as right_t
    	on (left_t.region = right_t.region)
    order by left_t.data_point, left_t.region, left_t.vac_interval_group
    '''
    inf_vac_columns = ['data_point', 'region', 'vac_interval_group', 'vaccine',

                       'count_vac_zab_18_59', 'count_vac_hosp_18_59', 'count_vac_severe_18_59', 'count_vac_death_18_59',
                       'count_vac_zab_60', 'count_vac_hosp_60', 'count_vac_severe_60', 'count_vac_death_60',

                       'count_zab_18_59', 'count_hosp_18_59', 'count_severe_18_59', 'count_death_18_59',
                       'count_zab_60', 'count_hosp_60', 'count_severe_60', 'count_death_60',

                       'count_vac_zab_total', 'count_vac_hosp_total', 'count_vac_severe_total', 'count_vac_death_total',
                       'count_zab_total', 'count_hosp_total', 'count_severe_total', 'count_death_total']

    vac_pop_columns = ['data_point', 'region', 'vac_interval_group', 'vaccine',
                       'vac_count_18_59', 'vac_count_60', 'vac_count_total',
                       'nas_age_18_59', 'nas_age_60', 'nas_age_adult_total']

    db_cursor = connect_to_db()
    inf_vac_df = query_to_df(inf_vac_q, db_cursor, inf_vac_columns)
    vac_pop_df = query_to_df(vac_pop_q, db_cursor, vac_pop_columns)
    # df_to_csv = inf_vac_df.merge(vac_pop_df, on=['data_point', 'region', 'vac_interval_group', 'vaccine'])
    # df_to_csv.to_csv('inf_vac.csv', sep=';', index=False, encoding='cp1251')

    inf_vac_grouped_df = add_aggregated_data(inf_vac_df)
    vac_pop_grouped_df = add_aggregated_data(vac_pop_df)

    pcv_df = compute_pcv(inf_vac_grouped_df)
    ppv_df = compute_ppv(vac_pop_grouped_df)
    ve = compute_ve(pcv_df, ppv_df)
    ve.to_csv('ve.csv', sep=';', index=False, encoding='cp1251')


if __name__ == '__main__':
    main()




