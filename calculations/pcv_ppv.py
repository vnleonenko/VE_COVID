import pandas as pd


def compute_pcv(inf_vac_data):
    pcv_columns = ['data_point', 'region', 'vac_interval_group', 'vaccine',
                   'pcv_zab_18_59', 'pcv_hosp_18_59', 'pcv_severe_18_59', 'pcv_death_18_59',
                   'pcv_zab_60', 'pcv_hosp_60', 'pcv_severe_60', 'pcv_death_60',
                   'pcv_zab_total', 'pcv_hosp_total', 'pcv_severe_total', 'pcv_death_total']
    pcv_df = pd.DataFrame(columns=pcv_columns)
    for pcv_column in pcv_columns:
        if pcv_column in inf_vac_data.columns:
            pcv_df[pcv_column] = inf_vac_data[pcv_column]
        else:
            case = pcv_column.split('_')[1]
            age = ''
            if '18_59' in pcv_column:
                age = '_18_59'
            elif '60' in pcv_column:
                age = '_60'
            elif 'total' in pcv_column:
                age = '_total'
            # print('count_vac_'+case+age)
            pcv_df[pcv_column] = inf_vac_data['count_vac_' + case + age] / inf_vac_data['count_' + case + age]
    return pcv_df


def compute_ppv(vac_pop_data):
    ppv_columns = ['data_point', 'region', 'vac_interval_group', 'vaccine',
                   'ppv_18_59', 'ppv_60', 'ppv_total']
    ppv_df = pd.DataFrame(columns=ppv_columns)
    for ppv_column in ppv_columns:
        if ppv_column in vac_pop_data.columns:
            ppv_df[ppv_column] = vac_pop_data[ppv_column]
        else:
            if '18_59' in ppv_column:
                pop_age = age = '_18_59'
            elif '60' in ppv_column:
                pop_age = age = '_60'
            else:
                age = '_total'
                pop_age = '_adult_total'
            ppv_df[ppv_column] = vac_pop_data['vac_count'+age] / vac_pop_data['nas_age'+pop_age]
    return ppv_df

