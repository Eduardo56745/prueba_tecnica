import pandas as pd
import psycopg2

# Leer datos extraídos
df = pd.read_parquet('raw_data.parquet')

# Renombrar columna 'name' → 'company_name'
df.rename(columns={'name': 'company_name'}, inplace=True)

# Agregar columna 'updated_at' con valor NULL o igual a 'paid_at'
df['updated_at'] = df['paid_at']

# Convertir NaT a None para que PostgreSQL acepte nulos
df['updated_at'] = df['updated_at'].where(pd.notnull(df['updated_at']), None)

df['amount'] = df['amount'].astype(float).round(2)
df['created_at'] = pd.to_datetime(df['created_at'])
df['updated_at'] = pd.to_datetime(df['updated_at'])

# Conexión a Postgres
conn = psycopg2.connect(
    dbname="mydatabase",
    user="myuser",
    password="mypassword",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Crear tabla destino
cur.execute("""
    DROP TABLE IF EXISTS cargo;
""")
cur.execute("""
    CREATE TABLE cargo (
        id VARCHAR(24) NOT NULL,
        company_name VARCHAR(130) NULL,
        company_id VARCHAR(24) NOT NULL,
        amount DECIMAL(16,2) NOT NULL,
        status VARCHAR(30) NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NULL
    );
""")
conn.commit()

# Insertar datos transformados
for row in df.itertuples():
    updated_at = row.updated_at if pd.notnull(row.updated_at) else None

cur.execute("""
    INSERT INTO cargo (id, company_name, company_id, amount, status, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
""", (
    row.id[:24],
    row.company_name[:130] if row.company_name else '',
    row.company_id[:24] if row.company_id else '',
    row.amount,
    row.status[:30] if row.status else '',
    row.created_at,
    updated_at
))


conn.commit()
cur.close()
conn.close()

print("✅ Transformación y carga completadas.")
