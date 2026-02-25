import duckdb

conn = duckdb.connect("market.db")

# Cambiar columnas de DATE a TIMESTAMP
conn.execute("""
    ALTER TABLE cars
    ALTER COLUMN first_seen SET DATA TYPE TIMESTAMP
""")

conn.execute("""
    ALTER TABLE cars
    ALTER COLUMN last_seen SET DATA TYPE TIMESTAMP
""")

# Si ya tienes columna sold creada como DATE
try:
    conn.execute("""
        ALTER TABLE cars
        ALTER COLUMN sold SET DATA TYPE TIMESTAMP
    """)
except:
    print("Columna sold no existe todavía")

print("✅ Migración completada")
