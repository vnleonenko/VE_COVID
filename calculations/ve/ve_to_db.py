from utils import connect_to_db
from tqdm import tqdm
import pandas as pd
import numpy as np
import pyodbc
import os


cnxn, crs = connect_to_db()

int_ve_folder_path = '../../app/data/input_csv_files/interval'
columns = ','.join(('data_point', 'region', 'vac_interval_group', 'vaccine',
                    've_zab_18_59', 'cil_zab_18_59', 'cih_zab_18_59',
                    've_hosp_18_59', 'cil_hosp_18_59', 'cih_hosp_18_59',
                    've_severe_18_59', 'cil_severe_18_59', 'cih_severe_18_59',
                    've_death_18_59', 'cil_death_18_59', 'cih_death_18_59',
                    've_zab_60', 'cil_zab_60', 'cih_zab_60',
                    've_hosp_60', 'cil_hosp_60', 'cih_hosp_60',
                    've_severe_60', 'cil_severe_60', 'cih_severe_60',
                    've_death_60', 'cil_death_60', 'cih_death_60',
                    've_zab_total', 'cil_zab_total', 'cih_zab_total',
                    've_hosp_total', 'cil_hosp_total', 'cih_hosp_total',
                    've_severe_total', 'cil_severe_total', 'cih_severe_total',
                    've_death_total', 'cil_death_total', 'cih_death_total'))


for file_path in tqdm(os.listdir(int_ve_folder_path)):
    file_path = os.path.join(int_ve_folder_path, file_path)
    data = pd.read_csv(file_path, encoding='cp1251', header=0, delimiter=';', decimal='.')
    data.iloc[:, 4:] = data.iloc[:, 4:].astype('float64')
    data = data.replace([np.nan, -np.inf, np.inf], None)
    values = ','.join(['?' for _ in range(len(data.columns))])
    insert_query = f'''insert into dbo.VE_W_VAC_INT values ({values})'''

    try:
        crs.executemany(insert_query, data.values.tolist())
    except pyodbc.IntegrityError:
        pass
cnxn.close()
