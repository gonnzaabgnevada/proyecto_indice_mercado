from playwright.sync_api import sync_playwright
import duckdb
import datetime
import time

# --------------------------
# DB
# --------------------------
conn = duckdb.connect("market.db")

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

BATCH_SIZE = 100
batch = []

def flush_batch():
    global batch
    if not batch:
        return

    conn.executemany("""
        INSERT INTO cars VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            last_seen = excluded.last_seen,
            price = excluded.price
    """, batch)

    batch = []

def add_to_batch(v):
    global batch
    today = datetime.date.today()

    batch.append((
        "https://www.coches.net" + v.get("link", ""),
        v.get("creationDate", ""),
        v.get("fuelType", ""),
        v.get("mainProvince", ""),
        v.get("make", ""),
        v.get("model", ""),
        v.get("price", 0),
        v.get("km", 0),
        v.get("title", ""),
        v.get("seller", {}).get("name", ""),
        v.get("seller", {}).get("isProfessional", False),
        today,
        today
    ))

    if len(batch) >= BATCH_SIZE:
        flush_batch()

# --------------------------
# SCRAPER
# --------------------------
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="es-ES",
        timezone_id="Europe/Madrid"
    )

    page = context.new_page()

    # stealth básico
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    """)

    page_number = 1

    while True:
        url = f"https://www.coches.net/segunda-mano/?pg={page_number}"
        print(f"\n➡ Página {page_number}")

        page.goto(url, wait_until="domcontentloaded")

        # Esperar a que exista la variable JS real
        try:
            page.wait_for_function("() => window.__INITIAL_PROPS__ !== undefined", timeout=15000)
        except:
            print("❌ No se encontró __INITIAL_PROPS__ (posible bloqueo)")
            break

        data = page.evaluate("() => window.__INITIAL_PROPS__")

        if not data:
            print("❌ Data es None")
            break

        # NUEVA estructura
        search = data.get("searchResults") or data.get("initialResults") or {}
        vehicles = search.get("items", [])

        if not vehicles:
            print("No quedan más vehículos.")
            break

        print(f"Vehículos encontrados: {len(vehicles)}")

        for v in vehicles:
            add_to_batch(v)

        page_number += 1
        time.sleep(0.5)  # pequeño delay humano

    flush_batch()
    browser.close()

print("\n🚀 Scraping completado correctamente.")
