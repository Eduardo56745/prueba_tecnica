import pandas as pd
import psycopg2

# Leer datos transformados
df = pd.read_parquet('raw_data.parquet')

# Renombrar columna 'name' → 'company_name'
df.rename(columns={'name': 'company_name'}, inplace=True)

# Asegurar columna 'updated_at'
df['updated_at'] = df['paid_at']
df['updated_at'] = df['updated_at'].where(pd.notnull(df['updated_at']), None)

# Asegurar tipos
df['amount'] = df['amount'].astype(float).round(2)
df['created_at'] = pd.to_datetime(df['created_at'])
df['updated_at'] = pd.to_datetime(df['updated_at'])

print("Shape después de leer y limpiar:", df.shape)
print(df.head())

# Conexión a Postgres
conn = psycopg2.connect(
    dbname="mydatabase",
    user="myuser",
    password="mypassword",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Limpiar tablas si existen
cur.execute("""DROP VIEW IF EXISTS daily_company_totals;""")
cur.execute("""DROP TABLE IF EXISTS charges;""")
cur.execute("""DROP TABLE IF EXISTS companies;""")

# Crear tabla companies
cur.execute("""
    CREATE TABLE companies (
        company_id VARCHAR(24) PRIMARY KEY,
        company_name VARCHAR(130)
    );
""")

# Crear tabla charges con llave foránea
cur.execute("""
    CREATE TABLE charges (
        id VARCHAR(24) PRIMARY KEY,
        company_id VARCHAR(24) NOT NULL REFERENCES companies(company_id),
        amount DECIMAL(30,2) NOT NULL,
        status VARCHAR(30) NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NULL
    );
""")
conn.commit()

# Agrupar compañías: único company_id
companies_df = (
    df[['company_id', 'company_name']]
    .dropna(subset=['company_id'])
    .groupby('company_id', as_index=False)
    .first()
)

print(f"Se insertarán {len(companies_df)} compañías")

for row in companies_df.itertuples():
    company_id = row.company_id[:24]
    company_name = row.company_name[:130] if pd.notnull(
        row.company_name) else None

    cur.execute("""
        INSERT INTO companies (company_id, company_name)
        VALUES (%s, %s)
    """, (company_id, company_name))

# Filtrar transacciones: sin id o company_id → fuera
df_clean = df.dropna(subset=['id', 'company_id'])
df_clean = df_clean[df_clean['amount'] < 1e28]

print(f"Se insertarán {len(df_clean)} charges")
print(df_clean.head())

for row in df_clean.itertuples():
    charge_id = row.id[:24]
    company_id = row.company_id[:24]
    updated_at = row.updated_at if pd.notnull(row.updated_at) else None

    cur.execute("""
        INSERT INTO charges (id, company_id, amount, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        charge_id,
        company_id,
        row.amount,
        row.status[:30],
        row.created_at,
        updated_at
    ))

conn.commit()
cur.close()
conn.close()

print("✅ Dispersión completada: datos cargados.")
