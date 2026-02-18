import duckdb
import datetime

conn = duckdb.connect("market.db")

today = datetime.date.today()

conn.execute("""
INSERT INTO cars VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "test_id",
    "BMW",
    "Serie 3",
    "320d",
    2019,
    120000,
    18000,
    "Madrid",
    "Profesional",
    "https://ejemplo.com",
    today,
    today
))

print("Insertado correctamente")
