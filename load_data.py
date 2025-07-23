import pandas as pd
import psycopg2

# Cargar el CSV
df = pd.read_csv('dataset.csv')

# Convertir columnas de fecha
df = df.where(pd.notnull(df), None)

# Filtrar valores absurdos
df.loc[df['amount'] < 1e6, 'amount'] = None

# Conexión a Postgres
conn = psycopg2.connect(
    dbname="mydatabase",
    user="myuser",
    password="mypassword",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS raw_data;")
conn.commit()

# Crear tabla temporal
cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_data (
        id VARCHAR(50),
        name VARCHAR(130),
        company_id VARCHAR(50),
        amount NUMERIC,
        status VARCHAR(30),
        created_at TIMESTAMP,
        paid_at TIMESTAMP
    );
""")
conn.commit()

# Insertar fila por fila
for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO raw_data (id, name, company_id, amount, status, created_at, paid_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        row['id'],
        row['name'],
        row['company_id'],
        row['amount'],
        row['status'],
        row['created_at'],
        row['paid_at']
    ))
conn.commit()

cur.close()
conn.close()
