import duckdb

# 🔹 Conexión a la base de datos
conn = duckdb.connect("market.db")

# 🔹 Crear tabla si no existe
conn.execute("""
CREATE TABLE IF NOT EXISTS cars (
    url VARCHAR PRIMARY KEY,
    creationDate VARCHAR,
    fuelType VARCHAR,
    mainProvince VARCHAR,
    make VARCHAR,
    model VARCHAR,
    price INTEGER,
    km INTEGER,
    title VARCHAR,
    seller_name VARCHAR,
    seller_isProfessional BOOLEAN,
    first_seen DATE,
    last_seen DATE
)
""")

print("Database ready")
