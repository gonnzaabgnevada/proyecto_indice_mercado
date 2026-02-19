from playwright.sync_api import sync_playwright
import duckdb
import datetime
import random
import time

# -------------------------
# CONFIGURACIÓN DE PÁGINAS
# -------------------------
PAGE_BLOCK = 1   # 👈 CAMBIA SOLO ESTO

PAGES_PER_BLOCK = 10
start_page = (PAGE_BLOCK - 1) * PAGES_PER_BLOCK + 1
end_page = PAGE_BLOCK * PAGES_PER_BLOCK

# Conectar/crear base de datos
conn = duckdb.connect("market.db")

# Crear tabla si no existe
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

def save_car(
    url, creationDate, fuelType, mainProvince, make, model, price, km,
    title, seller_name, seller_isProfessional
):
    today = datetime.date.today()

    existing = conn.execute(
        "SELECT url FROM cars WHERE url = ?",
        (url,)
    ).fetchone()

    if existing:
        conn.execute("""
            UPDATE cars
            SET last_seen = ?, price = ?
            WHERE url = ?
        """, (today, price, url))
    else:
        conn.execute("""
            INSERT INTO cars VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            url, creationDate, fuelType, mainProvince, make, model,
            price, km, title, seller_name, seller_isProfessional, today, today
        ))

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="es-ES",
        timezone_id="Europe/Madrid"
    )

    page = context.new_page()

    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """)

    try:
        for page_number in range(start_page, end_page + 1):

            print(f"\n➡ Scrapeando página {page_number}")

            url_page = f"https://www.coches.net/segunda-mano/?pg={page_number}"
            page.goto(url_page, wait_until="domcontentloaded")

            # Esperar a que React cargue los datos
            try:
                page.wait_for_function(
                    "() => window.__INITIAL_PROPS__ !== undefined",
                    timeout=15000
                )
            except:
                print("No se pudo cargar __INITIAL_PROPS__")
                continue

            data = page.evaluate("() => window.__INITIAL_PROPS__")

            if not data:
                print("Data vacía")
                continue

            vehicles = data.get("initialResults", {}).get("items", [])

            if not vehicles:
                print("No se encontraron vehículos")
                continue

            print("Vehículos encontrados:", len(vehicles))

            for v in vehicles:
                try:
                    link = v.get("url", "")
                    if not link:
                        continue

                    url = "https://www.coches.net" + link
                    creationDate = v.get("creationDate", "")
                    fuelType = v.get("fuelType", "")
                    location = v.get("location", {})
                    mainProvince = location.get("mainProvince", "")
                    make = v.get("make", "")
                    model = v.get("model", "")
                    price = v.get("price", 0)
                    km = v.get("km", 0)
                    title = v.get("title", "")

                    seller = v.get("seller", {})
                    seller_name = seller.get("name", "")
                    seller_isProfessional = seller.get("isProfessional", False)

                    save_car(
                        url, creationDate, fuelType, mainProvince,
                        make, model, price, km,
                        title, seller_name, seller_isProfessional
                    )

                    print("Saved:", title)
                    time.sleep(0.5)

                except Exception as e:
                    print("Error procesando vehículo:", e)

            # pequeño delay entre páginas
            time.sleep(random.uniform(2, 4))

    finally:
        browser.close()

print("\n🚀 Bloque completado correctamente.")
