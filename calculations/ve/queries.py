

def infected_merged_3_age_groups():
    return f'''
    set arithabort off;
    set ansi_warnings off;
    
    
    select *,
    sq5.count_zab_18_59 + sq5.count_zab_60 as count_zab_total,
    sq5.count_hosp_18_59 + sq5.count_hosp_60 as count_hosp_total,
    sq5.count_severe_18_59 + sq5.count_severe_60 as count_severe_total,
    sq5.count_death_18_59 + sq5.count_death_60 as count_death_total
    
    from
        (select sq4.data_point, sq4.region,
                sum(sq4.count_zab_18_59) as count_zab_18_59,
                sum(sq4.count_hosp_18_59) as count_hosp_18_59,
                sum(sq4.count_severe_18_59) as count_severe_18_59,
                sum(sq4.count_death_18_59) as count_death_18_59,
    
                sum(sq4.count_zab_60) as count_zab_60,
                sum(sq4.count_hosp_60) as count_hosp_60,
                sum(sq4.count_severe_60) as count_severe_60,
                sum(sq4.count_death_60) as count_death_60
        from
            (select sq3.data_point, sq3.region,
                case when sq3.age_group = '18-59' then sq3.count_zab  else 0 end as count_zab_18_59,
                case when sq3.age_group = '18-59' then sq3.count_hosp  else 0 end as count_hosp_18_59,
                case when sq3.age_group = '18-59' then sq3.count_severe  else 0 end as count_severe_18_59,
                case when sq3.age_group = '18-59' then sq3.count_death  else 0 end as count_death_18_59,
    
                case when sq3.age_group = '60+' then sq3.count_zab  else 0 end as count_zab_60,
                case when sq3.age_group = '60+' then sq3.count_hosp  else 0 end as count_hosp_60,
                case when sq3.age_group = '60+' then sq3.count_severe  else 0 end as count_severe_60,
                case when sq3.age_group = '60+' then sq3.count_death  else 0 end as count_death_60
    
            from
                (select sq2.data_point, sq2.region, sq2.age_group,
                sum(sq2.count_zab) as count_zab,
                sum(sq2.count_hosp) as count_hosp,
                sum(sq2.count_severe) as count_severe,
                sum(sq2.count_death) as count_death
                from
                    (select sq1.data_point,  sq1.region,
                    case when sq1.age_group in ('20-29', '30-39', '40-49', '50-59') then '18-59' else '60+' end as age_group,
                    sq1.count_zab, sq1.count_hosp, sq1.count_severe, sq1.count_death
                    from
                        (select data_point, region, age_group,
                                sum(count_zab) as count_zab, sum(count_hosp) as count_hosp,
                                sum(count_severe) as count_severe, sum(count_death) as count_death
                        from dbo.ZAB_VIEW
                        where data_point = '2022.08.B_16-09-2022' and age_group not in('0-9', '10-19')
                        group by data_point, region, age_group
                        ) as sq1
                    ) as sq2
                group by sq2.data_point, sq2.region, sq2.age_group
                ) as sq3
            ) as sq4
        group by sq4.data_point, sq4.region
    ) as sq5
    order by sq5.data_point, sq5.region'''


def inf_vaccinated_merged_3_age_groups():
    return f'''select sq5.*, 
                    sq5.count_vac_zab_18_59 + sq5.count_vac_zab_60 as count_vac_zab_total,
                    sq5.count_vac_hosp_18_59 + sq5.count_vac_hosp_60 as count_vac_hosp_total,
                    sq5.count_vac_severe_18_59 + sq5.count_vac_severe_60 as count_vac_severe_total,
                    sq5.count_vac_death_18_59 + sq5.count_vac_death_60 as count_vac_death_total
            from
                (select sq4.data_point, sq4.region, sq4.vac_interval_group, sq4.vaccine,
                    sum(count_vac_zab_18_59) as count_vac_zab_18_59, sum(count_vac_hosp_18_59) as count_vac_hosp_18_59,
                    sum(count_vac_severe_18_59) as count_vac_severe_18_59, sum(count_vac_death_18_59) as count_vac_death_18_59,
            
                    sum(count_vac_zab_60) as count_vac_zab_60, sum(count_vac_hosp_60) as count_vac_hosp_60,
                    sum(count_vac_severe_60) as count_vac_severe_60, sum(count_vac_death_60) as count_vac_death_60
                from 
                    (select sq3.data_point, sq3.region, sq3.vac_interval_group, sq3.vaccine,
                            case when sq3.age_group = '18-59' then sq3.count_vac_zab  else 0 end as count_vac_zab_18_59,
                            case when sq3.age_group = '18-59' then sq3.count_vac_severe  else 0 end as count_vac_severe_18_59,
                            case when sq3.age_group = '18-59' then sq3.count_vac_hosp  else 0 end as count_vac_hosp_18_59,
                            case when sq3.age_group = '18-59' then sq3.count_vac_death  else 0 end as count_vac_death_18_59,
            
                            case when sq3.age_group = '60+' then sq3.count_vac_zab  else 0 end as count_vac_zab_60,
                            case when sq3.age_group = '60+' then sq3.count_vac_hosp  else 0 end as count_vac_hosp_60,
                            case when sq3.age_group = '60+' then sq3.count_vac_severe  else 0 end as count_vac_severe_60,
                            case when sq3.age_group = '60+' then sq3.count_vac_death  else 0 end as count_vac_death_60
                    from 
                        (select sq2.data_point, sq2.region, sq2.vac_interval_group, sq2.vaccine, sq2.age_group,
                                sum(sq2.count_vac_zab) as count_vac_zab,
                                sum(sq2.count_vac_hosp) as count_vac_hosp,
                                sum(sq2.count_vac_severe) as count_vac_severe,
                                sum(sq2.count_vac_death) as count_vac_death
                        from
                            (select data_point, region, vac_interval_group, vaccine,
                            case when sq1.age_group in ('20-29', '30-39', '40-49', '50-59') then '18-59' else '60+' end as age_group,
                            count_vac_zab, count_vac_hosp, count_vac_severe, count_vac_death
                            from
                                (select data_point, region, vac_interval_group, vaccine, age_group,
                                        sum(count_vac_zab) as count_vac_zab, sum(count_vac_hosp) as count_vac_hosp,
                                        sum(count_vac_severe) as count_vac_severe, sum(count_vac_death) as count_vac_death
                                from dbo.ZAB_VAC_VIEW
                                where data_point = '2022.08.B_16-09-2022' and age_group not in('0-9', '10-19')
                                group by data_point, region, vac_interval_group, vaccine, age_group
                                ) as sq1
                            ) as sq2
                        group by sq2.data_point, sq2.region, sq2.vac_interval_group, sq2.vaccine, sq2.age_group
                        ) as sq3
                    ) as sq4
                group by sq4.data_point, sq4.region, sq4.vac_interval_group, sq4.vaccine
            ) as sq5
            order by sq5.data_point, sq5.region, sq5.vaccine'''


def vaccinated_merged_3_age_groups():
    return f'''select sq5.*, sq5.vac_count_18_59 + sq5.vac_count_60 as vac_count_total
            from
                (select sq4.data_point, sq4.region, sq4.vac_interval_group, sq4.vaccine,
                sum(sq4.vac_count_18_59) as vac_count_18_59,
                sum(sq4.vac_count_60) as vac_count_60
                from
                    (select sq3.data_point, sq3.region, sq3.vac_interval_group, sq3.vaccine, 
                    case when sq3.age_group = '18-59' then sq3.vac_count else 0 end as vac_count_18_59,
                    case when sq3.age_group = '60+' then sq3.vac_count else 0 end as vac_count_60
                    from
                        (select sq2.data_point, sq2.region, sq2.vac_interval_group, sq2.vaccine, sq2.age_group,
                        sum(sq2.vac_count) as vac_count
                        from
                            (select sq1.data_point, sq1.region, sq1.vac_interval_group, sq1.vaccine,
                            case when sq1.age_group in ('20-29', '30-39', '40-49', '50-59') then '18-59' else '60+' end as age_group,
                            sq1.vac_count
                            from
                                (select data_point, region, vac_interval_group, vaccine, age_group, sum(vac_count) as vac_count
                                from dbo.VAC_VIEW
                                where data_point = '2022.08.B_16-09-2022' and age_group not in ('0-9', '10-19')
                                group by data_point, region, vac_interval_group, vaccine, age_group
                                ) as sq1
                            ) as sq2
                        group by sq2.data_point, sq2.region, sq2.vac_interval_group, sq2.vaccine, sq2.age_group
                    ) as sq3
                ) as sq4 
                group by sq4.data_point, sq4.region, sq4.vac_interval_group, sq4.vaccine
                ) as sq5
            order by sq5.data_point, sq5.region, sq5.vac_interval_group'''


def vaccinated_3_age_groups():
    return '''
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


def infected_3_age_groups():
    return '''select sq3.*,
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
                
                    (select data_point, region, age_group, 
                            sum(count_zab) as count_zab, sum(count_hosp) as count_hosp, 
                            sum(count_severe) as count_severe, sum(count_death) as count_death
                    from dbo.ZAB_VIEW
                    where data_point not like '%[B]%' and age_group <> '17-'
                    group by data_point, region, age_group) as sq1
                ) as sq2
                group by sq2.data_point, sq2.region) as sq3
            order by sq3.data_point, sq3.region'''


def inf_vaccinated_3_age_groups():
    return '''select sq3.*, 
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
            order by sq3.data_point, sq3.region, sq3.vac_interval_group, sq3.vaccine'''


def population():
    return '''select region, nas_age_18_59_total, nas_age_60_total, nas_age_adult_total 
              from dbo.NAS_AGE'''




