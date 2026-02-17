import duckdb

conn = duckdb.connect("market.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS cars (
    vehicle_id VARCHAR,
    make VARCHAR,
    model VARCHAR,
    engine VARCHAR,
    year INTEGER,
    km INTEGER,
    price INTEGER,
    province VARCHAR,
    seller_type VARCHAR,
    link VARCHAR,
    first_seen DATE,
    last_seen DATE
)
""")

print("Database ready")