import pyodbc
import numpy as np
import pandas as pd
from tqdm import tqdm
from connector import MSSQLConnector


if __name__ == "__main__":
    csv_path = '../output/ve/ve_3_1_new_dates.csv'

    ve_df = pd.read_csv(csv_path, encoding='cp1251', delimiter=';')
    ve_df.iloc[:, 5:] = ve_df.iloc[:, 5:].astype('float64')
    ve_df = ve_df.replace([np.nan, -np.inf, np.inf], None)
    table_name = 'dbo.VE_TEST'
    values = ','.join(['?' for _ in range(len(ve_df.columns))])
    insert_query = f'''insert into {table_name} values ({values})'''

    with MSSQLConnector() as con:
        for i in tqdm(range(ve_df.shape[0])):
            try:
                con.cursor.execute(insert_query, ve_df.iloc[i, :].tolist())
            except pyodbc.IntegrityError as e:
                print(e)
