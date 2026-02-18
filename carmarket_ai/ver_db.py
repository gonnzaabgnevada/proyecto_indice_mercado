import os
import duckdb
from tabulate import tabulate

db_path = os.path.join(os.path.dirname(__file__), "market.db")
conn = duckdb.connect(db_path)

registros = conn.execute("SELECT * FROM cars").fetchall()
columnas = [col[1] for col in conn.execute("PRAGMA table_info('cars')").fetchall()]

print(tabulate(registros, headers=columnas, tablefmt="fancy_grid"))
