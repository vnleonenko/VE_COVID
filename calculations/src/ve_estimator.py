import numpy as np
import pandas as pd
from tqdm import tqdm
import statsmodels.api as sm
import statsmodels.formula.api as smf
tqdm.pandas()


class VEEstimator:
    def __init__(self, inf_df, vac_df, inf_vac_df, pop_df):
        self.inf = inf_df
        self.vac = vac_df
        self.inf_vac = inf_vac_df
        self.pop = pop_df

    def _compute_ppv(self):
        columns = ['data_point', 'region', 'age_group', 'vac_interval_group', 'vaccine']
        ppv_df = self.vac.loc[:, columns]
        vac_pop_df = self.vac.merge(self.pop, on=['region', 'age_group'], how='left')
        wo_all_vaccines = vac_pop_df[~(vac_pop_df['vaccine'] == 'AllVaccines')]
        grouped_vac_pop = wo_all_vaccines.groupby(['data_point', 'region', 'vac_interval_group',
                                         'age_group'], as_index=False).agg({'vac_count': 'sum',
                                                                            'population': lambda x: x.iloc[0]})
        merged_vac_pop = wo_all_vaccines.merge(grouped_vac_pop, on=['data_point', 'region', 'vac_interval_group',
                                        'age_group', 'population'], how='left', suffixes=('', '_sum'))
        merged_vac_pop['population'] = merged_vac_pop['population'] - merged_vac_pop['vac_count_sum'] + \
                                       merged_vac_pop['vac_count']
        merged_vac_pop = merged_vac_pop.drop('vac_count_sum', axis=1)
        vac_pop_df_corrected = pd.concat([vac_pop_df[vac_pop_df['vaccine'] == 'AllVaccines'], merged_vac_pop])
        vac_pop_df_corrected = vac_pop_df_corrected.sort_values(by=['data_point', 'region', 'age_group', 'vaccine'],
                                                                ignore_index=True)

        '''vac_pop_df['population'] = vac_pop_df[vac_pop_df.columns.values].progress_apply(lambda row:
                                              self._ppv_correction(vac_pop_df, row), axis=1, result_type="expand")'''
        ppv_df['ppv'] = vac_pop_df_corrected['vac_count'] / vac_pop_df_corrected['population']
        ppv_df['ppv'] = ppv_df['ppv'].astype('float32')
        return ppv_df

    @staticmethod
    def get_ve_w_ci(args):
        case, vac_case, ppv = int(args[0]), int(args[1]), args[2]
        df = pd.DataFrame(columns=['case', 'vac_case', 'ppv'])
        df['y'] = [1 if (i <= vac_case) and (i != 0) else 0 for i in range(case)]
        if ppv == 0:
            return np.nan, np.nan, np.nan

        df['logit_ppv'] = np.log(ppv / (1 - ppv))
        df = df.fillna({'case': case, 'vac_case': vac_case, 'ppv': ppv})
        glm = smf.glm(formula='y ~ 1', data=df, offset=df['logit_ppv'],
                      family=sm.families.Binomial())
        glm_res = glm.fit()
        ve_estimation = round(1 - np.exp(glm_res.params).values[0], 5)
        ci = [round(ci, 5) for ci in 1 - np.exp(glm_res.conf_int(alpha=0.05)).values[0]]
        return ve_estimation, ci[1], ci[0]

    def compute_ve(self):
        ppv_data = self._compute_ppv()
        inf_vac_merged = self.inf_vac.merge(self.inf, on=['data_point', 'age_group', 'region'], how='left')
        wo_all_vac = inf_vac_merged[~(inf_vac_merged['vaccine'] == 'AllVaccines')]
        grouped_inf_vac = wo_all_vac.groupby(['data_point', 'region', 'vac_interval_group', 'age_group'],
                                             as_index=False).agg({'count_vac_zab': 'sum', 'count_vac_hosp': 'sum',
                                                                  'count_vac_severe': 'sum', 'count_vac_death': 'sum',
                                                                  'count_zab': lambda x: x.iloc[0],
                                                                  'count_hosp': lambda x: x.iloc[0],
                                                                  'count_severe': lambda x: x.iloc[0],
                                                                  'count_death': lambda x: x.iloc[0]})
        inf_vac_df_cor = wo_all_vac.merge(grouped_inf_vac, on=['data_point', 'region', 'vac_interval_group',
                                                               'age_group', 'count_zab', 'count_hosp',
                                                               'count_severe', 'count_death'], how='left',
                                          suffixes=('', '_sum'))
        cases = ['zab', 'hosp', 'severe', 'death']
        for case in cases:
            inf_vac_df_cor['count_' + case] = inf_vac_df_cor['count_' + case] - \
                                              inf_vac_df_cor[f'count_vac_{case}_sum'] + \
                                              inf_vac_df_cor[f'count_vac_{case}']
            inf_vac_df_cor = inf_vac_df_cor.drop(f'count_vac_{case}_sum', axis=1)

        inf_vac_df_cor = pd.concat([inf_vac_merged[inf_vac_merged['vaccine'] == 'AllVaccines'], inf_vac_df_cor])
        inf_vac_df_cor = inf_vac_df_cor.sort_values(by=['data_point', 'region', 'age_group', 'vaccine'],
                                                    ignore_index=True)

        merge_columns = ['data_point', 'region', 'age_group', 'vac_interval_group', 'vaccine']
        merged_df = ppv_data.merge(inf_vac_df_cor, on=merge_columns, how='outer')
        merged_df.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

        # filter columns that should be integer
        int_columns = list(filter(lambda x: x not in merge_columns+['ppv'], merged_df.columns))
        # optimize DataFrame size by casting
        merged_df.loc[:, merge_columns] = merged_df.loc[:, merge_columns].astype('category')
        merged_df.loc[:, int_columns] = merged_df.loc[:, int_columns].astype('int32')

        ve_df = merged_df.loc[:, merge_columns]
        for case in tqdm(cases):
            print(f'Calculations for {case} cases have been started')
            inf_column = 'count_' + case
            inf_vac_column = 'count_vac_' + case
            ppv_column = 'ppv'
            ve_df[['ve_'+case, 'cil_'+case, 'cih_'+case]] = merged_df[[inf_column, inf_vac_column, ppv_column]]\
                .progress_apply(lambda x: self.get_ve_w_ci(x) if np.all(x[:2]) != 0
                                else [np.nan, np.nan, np.nan], axis=1, result_type="expand")
            # ve_df.to_csv(f'../output/ve_{case}.csv', sep=';', index=False, encoding='cp1251', na_rep='NULL')

        return ve_df
