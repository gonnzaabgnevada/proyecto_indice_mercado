import duckdb

conn = duckdb.connect()

# Cargar CSV principal
conn.execute("""
CREATE TABLE cars AS
SELECT * FROM read_csv_auto('cars.csv');
""")

# Cargar CSV nuevo
conn.execute("""
CREATE TABLE cars_new AS
SELECT * FROM read_csv_auto('cars_132_urls.csv');
""")

# Insertar solo los que NO existen en cars
conn.execute("""
INSERT INTO cars
SELECT *
FROM cars_new n
WHERE NOT EXISTS (
    SELECT 1 FROM cars c
    WHERE c.url = n.url
);
""")

# Exportar resultado final sobrescribiendo el principal
conn.execute("""
COPY cars TO 'cars.csv' (HEADER, DELIMITER ',');
""")

print("Datos fusionados correctamente sin duplicados.")
