import pandas as pd


class DataProcessor:
    def __init__(self, cursor):
        self.cursor = cursor

    def query_to_df(self, query, columns):
        query_res = list(map(list, self.cursor.execute(query).fetchall()))
        df = pd.DataFrame(query_res, columns=columns)
        sort_columns = list(filter(lambda x: 'count' not in x, columns))
        df.sort_values(by=sort_columns, inplace=True, ignore_index=True)
        return df

