import psycopg2

# Configuración de conexión
conn = psycopg2.connect(
    dbname="mydatabase",
    user="myuser",
    password="mypassword",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Crear o reemplazar la vista
cur.execute("""
CREATE OR REPLACE VIEW daily_amounts_by_company AS
SELECT
    company_id,
    DATE(created_at) AS transaction_date,
    SUM(amount) AS total_amount
FROM
    charges
GROUP BY
    company_id,
    DATE(created_at)
ORDER BY
    company_id,
    transaction_date;
""")

conn.commit()
cur.close()
conn.close()

print("✅ Vista daily_amounts_by_company creada o actualizada.")
