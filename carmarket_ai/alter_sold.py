import duckdb

# Conectamos a la base de datos
conn = duckdb.connect("market.db")

# Actualizamos todos los registros para poner sold a NULL
conn.execute("""
    UPDATE cars
    SET sold = NULL
""")

print("✅ Todos los valores de 'sold' han sido reseteados a NULL")
