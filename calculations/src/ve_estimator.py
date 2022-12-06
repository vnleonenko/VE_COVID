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
        ppv_df['ppv'] = vac_pop_df['vac_count'] / vac_pop_df['population']
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
        merge_columns = ['data_point', 'region', 'age_group', 'vac_interval_group', 'vaccine']
        merged_df = ppv_data.merge(inf_vac_merged, on=merge_columns, how='outer')
        merged_df.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

        # filter columns that should be integer
        int_columns = list(filter(lambda x: x not in merge_columns+['ppv'], merged_df.columns))

        # optimize DataFrame size by casting
        merged_df.loc[:, merge_columns] = merged_df.loc[:, merge_columns].astype('category')
        merged_df.loc[:, int_columns] = merged_df.loc[:, int_columns].astype('int32')

        ve_df = merged_df.loc[:, merge_columns]
        cases = ['zab', 'hosp', 'severe', 'death']
        for case in tqdm(cases):
            print(f'Calculations for {case} cases have been started')
            inf_column = 'count_' + case
            inf_vac_column = 'count_vac_' + case
            ppv_column = 'ppv'
            ve_df[['ve', 'cil', 'cih']] = merged_df[[inf_column, inf_vac_column, ppv_column]].progress_apply(
                                          lambda x: self.get_ve_w_ci(x) if np.all(x[:2]) != 0
                                          else [np.nan, np.nan, np.nan], axis=1, result_type="expand")
        '''ve_df.to_csv(f'calculations/output/jan22/{merged_df["data_point"][0]}_ve_w_ci.csv',
                     sep=';', index=False, encoding='cp1251', na_rep='NULL')'''
        return ve_df
