import os
import duckdb

# Conectarse a la base de datos
db_path = os.path.join(os.path.dirname(__file__), "market.db")
conn = duckdb.connect(db_path)

# Mostrar columnas de la tabla cars
columnas = conn.execute("PRAGMA table_info('cars')").fetchall()

print("Columnas de la tabla 'cars':")
for col in columnas:
    print(f"Nombre: {col[1]}, Tipo: {col[2]}")
