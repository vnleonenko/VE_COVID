import pyodbc
import pandas as pd

server = 'tcp:db.influenza.spb.ru,1984'
database = 'VE'
username = 've_access'
password = 'VE@niiGrippa4$'
cnxn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};'
                      'SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = cnxn.cursor()

ppv_3_age_groups_q = '''
select left_t.data_point, left_t.region, left_t.vac_interval_group, 
--right_t.nas_age_18_59_total, right_t.nas_age_60_total, right_t.nas_age_adult_total,
cast(left_t.vac_count_18_59 * 1.00 / right_t.nas_age_18_59_total as decimal(8, 5)) as ppv_18_59,
cast(left_t.vac_count_60 * 1.00 / right_t.nas_age_60_total as decimal(8, 5)) as ppv_60,
cast(left_t.vac_count_total * 1.00 / right_t.nas_age_adult_total as decimal(8, 5)) as ppv_total
from
	(select *, sq3.vac_count_18_59 + sq3.vac_count_60 as vac_count_total
	from
		(select sq2.data_point, sq2.region, sq2.vac_interval_group,
		sum(sq2.vac_count_18_59) as vac_count_18_59,
		sum(sq2.vac_count_60) as vac_count_60
		from 
			(select sq1.data_point, sq1.region, sq1.vac_interval_group,
			case when sq1.age_group = '18-59' then sq1.vac_count else 0 end as vac_count_18_59,
			case when sq1.age_group = '60+' then sq1.vac_count else 0 end as vac_count_60
			from
				(select  data_point, region, vac_interval_group,
				age_group, sum(vac_count) as vac_count
				from dbo.VAC_VIEW
				where data_point not like '%[B]%' and age_group <> '17-'
				group by data_point, region, vac_interval_group, age_group
				) as sq1
			) as sq2
			group by sq2.data_point, sq2.region, sq2.vac_interval_group
		) as sq3
	) as left_t
	left join 
		(select region, nas_age_18_59_total, nas_age_60_total, nas_age_adult_total 
		from dbo.NAS_AGE) as right_t
	on (left_t.region = right_t.region)
order by left_t.data_point, left_t.region, left_t.vac_interval_group
'''

pcv_3_age_groups_q = '''
set arithabort off;
set ansi_warnings off;

select res_pcv.*,
res_pcv.pcv_zab_18_59 + res_pcv.pcv_zab_60 as pcv_zab_total,
res_pcv.pcv_hosp_18_59 + res_pcv.pcv_hosp_60 as pcv_hosp_total,
res_pcv.pcv_severe_18_59 + res_pcv.pcv_severe_60 as pcv_severe_total,
res_pcv.pcv_death_18_59 + res_pcv.pcv_death_60 as pcv_death_total
from
	(select agg_pcv.data_point, agg_pcv.region, agg_pcv.vac_interval_group, agg_pcv.vaccine, 
	sum(pcv_zab_18_59) as pcv_zab_18_59, sum(pcv_hosp_18_59) as pcv_hosp_18_59,
	sum(pcv_severe_18_59) as pcv_severe_18_59, sum(pcv_death_18_59) as pcv_death_18_59,

	sum(pcv_zab_60) as pcv_zab_60, sum(pcv_hosp_60) as pcv_hosp_60,
	sum(pcv_severe_60) as pcv_severe_60, sum(pcv_death_60) as pcv_death_60

	from
		(select left_t.*, right_t.count_zab, right_t.count_hosp, 
		right_t.count_severe, right_t.count_death,
		case when left_t.age_group = '18-59' then cast((left_t.count_vac_zab * 1.00 / right_t.count_zab) as decimal(8, 5)) else 0 end as pcv_zab_18_59,
		case when left_t.age_group = '18-59' then cast((left_t.count_vac_hosp * 1.00 / right_t.count_hosp) as decimal(8, 5)) else 0 end as pcv_hosp_18_59,
		case when left_t.age_group = '18-59' then cast((left_t.count_vac_severe * 1.00 / right_t.count_severe) as decimal(8, 5)) else 0 end as pcv_severe_18_59,
		case when left_t.age_group = '18-59' then cast((left_t.count_vac_death * 1.00 / right_t.count_death) as decimal(8, 5)) else 0 end as pcv_death_18_59,

		case when left_t.age_group = '60+' then cast((left_t.count_vac_zab * 1.00 / right_t.count_zab) as decimal(8, 5)) else 0 end as pcv_zab_60,
		case when left_t.age_group = '60+' then cast((left_t.count_vac_hosp * 1.00 / right_t.count_hosp) as decimal(8, 5)) else 0 end as pcv_hosp_60,
		case when left_t.age_group = '60+' then cast((left_t.count_vac_severe * 1.00 / right_t.count_severe) as decimal(8, 5)) else 0 end as pcv_severe_60,
		case when left_t.age_group = '60+' then cast((left_t.count_vac_death * 1.00 / right_t.count_death) as decimal(8, 5)) else 0 end as pcv_death_60

		from
			(select data_point, region, vac_interval_group,
					vaccine, age_group,
					sum(count_vac_zab) as count_vac_zab, 
					sum(count_vac_hosp) as count_vac_hosp,
					sum(count_vac_severe) as count_vac_severe, 
					sum(count_vac_death) as count_vac_death
			from dbo.ZAB_VAC_VIEW
			where data_point not like '%[B]%' and age_group <> '17-'
			group by data_point, region, vac_interval_group, vaccine, age_group) as left_t
		left join
			(select data_point, region, age_group,
			sum(count_zab) as count_zab, 
			sum(count_hosp) as count_hosp, 
			sum(count_severe) as count_severe, 
			sum(count_death) as count_death
			from dbo.ZAB_VIEW
			where data_point not like '%[B]%' and age_group <> '17-'
			group by data_point, region, age_group) as right_t
		on (left_t.data_point = right_t.data_point) and (left_t.region = right_t.region) and (left_t.age_group = right_t.age_group)
		) as agg_pcv
	group by agg_pcv.data_point, agg_pcv.region, agg_pcv.vac_interval_group, agg_pcv.vaccine
	) as res_pcv
order by res_pcv.data_point, res_pcv.region, res_pcv.vac_interval_group, res_pcv.vaccine
'''


def convert_to_df(cursor_obj, query, column_names):
    query_result = list(map(list, cursor_obj.execute(query).fetchall()))
    return pd.DataFrame(query_result, columns=column_names)


pcv_columns = ['data_point', 'region', 'vac_interval_group', 'vaccine',
               'pcv_zab_18_59', 'pcv_hosp_18_59', 'pcv_severe_18_59', 'pcv_death_18_59',
               'pcv_zab_60', 'pcv_hosp_60', 'pcv_severe_60', 'pcv_death_60',
               'pcv_zab_total', 'pcv_hosp_total', 'pcv_severe_total', 'pcv_death_total']
ppv_columns = ['data_point', 'region', 'vac_interval_group',
               'ppv_18_59', 'ppv_60', 'ppv_total']
pcv_df = convert_to_df(cursor, pcv_3_age_groups_q, pcv_columns)
ppv_df = convert_to_df(cursor, ppv_3_age_groups_q, ppv_columns)


def calc_ve(ppv, pcv, data_point, region, vac_interval_group, vaccine, age, case):
    age_prefix = ' '
    if age == '18-59':
        age_prefix = '_18_59'
    elif age == '60+':
        age_prefix = '_60'
    factor_ppv = ppv.query(f'data_point=="{data_point}" & region=="{region}" '
                           f'& vac_interval_group=="{vac_interval_group}"')
    factor_ppv = factor_ppv['ppv' + age_prefix]
    factor_pcv = pcv.query(f'data_point=="{data_point}" & region=="{region}" '
                           f'& vac_interval_group=="{vac_interval_group}"'
                           f'& vaccine=="{vaccine}"')
    factor_pcv = factor_pcv['pcv_' + case + age_prefix]
    print(factor_pcv)
    print(type(factor_ppv))
    if len(factor_pcv) != 0:
        factor_pcv = factor_pcv.values[0]
    if len(factor_ppv) != 0:
        factor_ppv = factor_ppv.values[0]
    print('factor_ppv', factor_ppv.values)
    print('factor_pcv', factor_pcv.values)

    ve = 1 - (factor_pcv / (1 - factor_pcv)) * \
        ((1 - factor_ppv) / factor_ppv)
    return round(ve, 5)


print(calc_ve(ppv_df, pcv_df, '2021.11_01-07-2022', 'Алтайский край', '45_75_days', 'CoviVac', '18-59', 'zab'))
print(0.85577+0)