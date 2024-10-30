import pandas as pd
import duckdb

df_from_csv = pd.read_csv('./data_folder/ashaar.csv')
query = """
SELECT *
FROM df_from_csv
WHERE "poet name" = 'المتنبي'
LIMIT 10
"""
print(duckdb.sql(query).to_df())