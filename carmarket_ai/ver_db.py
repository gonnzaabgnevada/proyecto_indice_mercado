import os
import duckdb
import pandas as pd
from tabulate import tabulate
import pygsheets

# -----------------------------
# Conexión a la base de datos
# -----------------------------
db_path = os.path.join(os.path.dirname(__file__), "market.db")
conn = duckdb.connect(db_path)

columnas = [
    "creationDate", "fuelType", "mainProvince", "make", "model",
    "price", "km", "title", "url", "seller_name", "seller_isProfessional",
    "first_seen", "last_seen"
]

df = conn.execute(f"SELECT {', '.join(columnas)} FROM cars").fetchdf()

# -----------------------------
# Mostrar tabla en consola
# -----------------------------
df_mini = df.copy()
df_mini["url"] = df_mini["url"].apply(lambda x: x[:40] + "..." if len(x) > 40 else x)
print(tabulate(df_mini, headers=columnas, tablefmt="simple"))
print(f"\nTotal de tuplas en la tabla 'cars': {len(df)}\n")

csv_path = os.path.join(os.path.dirname(__file__), "cars.csv")
df.to_csv(csv_path, index=False, encoding="utf-8-sig")  # index=False evita que se agregue una columna de índice
print(f"✅ CSV exportado correctamente en: {csv_path}")