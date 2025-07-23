import pandas as pd
import psycopg2

conn = psycopg2.connect(
    dbname="mydatabase",
    user="myuser",
    password="mypassword",
    host="localhost",
    port="5432"
)

query = "SELECT * FROM raw_data;"

df = pd.read_sql(query, conn)

df.to_parquet('raw_data.parquet')

conn.close()
