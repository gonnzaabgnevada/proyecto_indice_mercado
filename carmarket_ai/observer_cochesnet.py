from playwright.sync_api import sync_playwright
import duckdb
import datetime
import time

# -------------------------
# CONFIGURACIÓN DE PÁGINAS
# -------------------------
START_PAGE = 1
END_PAGE = 30

# -------------------------
# LISTA COMPLETA DE 132 URLs (CON REPETIDOS)
# -------------------------
BASE_URLS = [
    "https://www.coches.net/search/?MinPrice=7000&arrProvince=28&MinYear=2015"
]

# -------------------------
# BASE DE DATOS
# -------------------------
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
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    sold TIMESTAMP
)
""")

def save_car(
    url, creationDate, fuelType, mainProvince, make, model, price, km,
    title, seller_name, seller_isProfessional
):
    now = datetime.datetime.now()

    existing = conn.execute(
        "SELECT url FROM cars WHERE url = ?",
        (url,)
    ).fetchone()

    if existing:
        conn.execute("""
            UPDATE cars
            SET last_seen = ?, 
                price = ?
            WHERE url = ?
        """, (now, price, url))
    else:
        conn.execute("""
            INSERT INTO cars VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            url, creationDate, fuelType, mainProvince, make, model,
            price, km, title, seller_name, seller_isProfessional,
            now, now, None
        ))


# -------------------------
# SCRAPER
# -------------------------
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

    page.set_default_navigation_timeout(60000)
    page.set_default_timeout(60000)

    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """)

    try:
        for base_url in BASE_URLS:

            print(f"\n==============================")
            print(f"🚗 URL base: {base_url}")
            print(f"==============================")

            for page_number in range(START_PAGE, END_PAGE + 1):

                url_page = f"{base_url}&pg={page_number}"
                print(f"\n➡ Scrapeando {url_page}")

                page.goto(url_page, wait_until="domcontentloaded")

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
                        time.sleep(1)

                    except Exception as e:
                        print("Error procesando vehículo:", e)

                time.sleep(8)  # pequeña pausa entre páginas

            # 👇 AQUÍ VA LA ESPERA DE 2 MINUTOS
            print("⏳ Esperando 2 minutos antes de la siguiente URL...")
            time.sleep(120)

    finally:
        browser.close()


print("\n🚀 Proceso completado correctamente.")
