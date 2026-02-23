from playwright.sync_api import sync_playwright
import duckdb
import datetime
import time

# -------------------------
# CONFIGURACIÓN DE PÁGINAS
# -------------------------
START_PAGE = 1
END_PAGE = 6

# -------------------------
# LISTA COMPLETA DE 132 URLs (CON REPETIDOS)
# -------------------------
BASE_URLS = [
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=8",
    "https://www.coches.net/search/?arrProvince=46",
    "https://www.coches.net/search/?arrProvince=41",
    "https://www.coches.net/search/?arrProvince=3",
    "https://www.coches.net/search/?arrProvince=29",
    "https://www.coches.net/search/?arrProvince=30",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=18",
    "https://www.coches.net/search/?arrProvince=48",
    "https://www.coches.net/search/?arrProvince=15",
    "https://www.coches.net/search/?arrProvince=7",
    "https://www.coches.net/search/?arrProvince=31",
    "https://www.coches.net/search/?arrProvince=47",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=8",
    "https://www.coches.net/search/?arrProvince=11",
    "https://www.coches.net/search/?arrProvince=45",
    "https://www.coches.net/search/?arrProvince=9",
    "https://www.coches.net/search/?arrProvince=39",
    "https://www.coches.net/search/?arrProvince=13",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=46",
    "https://www.coches.net/search/?arrProvince=43",
    "https://www.coches.net/search/?arrProvince=4",
    "https://www.coches.net/search/?arrProvince=14",
    "https://www.coches.net/search/?arrProvince=17",
    "https://www.coches.net/search/?arrProvince=23",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=8",
    "https://www.coches.net/search/?arrProvince=41",
    "https://www.coches.net/search/?arrProvince=3",
    "https://www.coches.net/search/?arrProvince=29",
    "https://www.coches.net/search/?arrProvince=30",
    "https://www.coches.net/search/?arrProvince=20",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=18",
    "https://www.coches.net/search/?arrProvince=33",
    "https://www.coches.net/search/?arrProvince=6",
    "https://www.coches.net/search/?arrProvince=36",
    "https://www.coches.net/search/?arrProvince=21",
    "https://www.coches.net/search/?arrProvince=24",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=8",
    "https://www.coches.net/search/?arrProvince=46",
    "https://www.coches.net/search/?arrProvince=50",
    "https://www.coches.net/search/?arrProvince=12",
    "https://www.coches.net/search/?arrProvince=25",
    "https://www.coches.net/search/?arrProvince=27",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=41",
    "https://www.coches.net/search/?arrProvince=3",
    "https://www.coches.net/search/?arrProvince=29",
    "https://www.coches.net/search/?arrProvince=30",
    "https://www.coches.net/search/?arrProvince=11",
    "https://www.coches.net/search/?arrProvince=45",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=8",
    "https://www.coches.net/search/?arrProvince=37",
    "https://www.coches.net/search/?arrProvince=1",
    "https://www.coches.net/search/?arrProvince=2",
    "https://www.coches.net/search/?arrProvince=26",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=46",
    "https://www.coches.net/search/?arrProvince=18",
    "https://www.coches.net/search/?arrProvince=10",
    "https://www.coches.net/search/?arrProvince=19",
    "https://www.coches.net/search/?arrProvince=22",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=8",
    "https://www.coches.net/search/?arrProvince=43",
    "https://www.coches.net/search/?arrProvince=4",
    "https://www.coches.net/search/?arrProvince=14",
    "https://www.coches.net/search/?arrProvince=17",
    "https://www.coches.net/search/?arrProvince=23",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=41",
    "https://www.coches.net/search/?arrProvince=3",
    "https://www.coches.net/search/?arrProvince=29",
    "https://www.coches.net/search/?arrProvince=30",
    "https://www.coches.net/search/?arrProvince=49",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=8",
    "https://www.coches.net/search/?arrProvince=46",
    "https://www.coches.net/search/?arrProvince=11",
    "https://www.coches.net/search/?arrProvince=45",
    "https://www.coches.net/search/?arrProvince=5",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=18",
    "https://www.coches.net/search/?arrProvince=34",
    "https://www.coches.net/search/?arrProvince=40",
    "https://www.coches.net/search/?arrProvince=44",
    "https://www.coches.net/search/?arrProvince=42",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=8",
    "https://www.coches.net/search/?arrProvince=48",
    "https://www.coches.net/search/?arrProvince=15",
    "https://www.coches.net/search/?arrProvince=7",
    "https://www.coches.net/search/?arrProvince=16",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=46",
    "https://www.coches.net/search/?arrProvince=41",
    "https://www.coches.net/search/?arrProvince=3",
    "https://www.coches.net/search/?arrProvince=29",
    "https://www.coches.net/search/?arrProvince=30",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=8",
    "https://www.coches.net/search/?arrProvince=43",
    "https://www.coches.net/search/?arrProvince=4",
    "https://www.coches.net/search/?arrProvince=14",
    "https://www.coches.net/search/?arrProvince=17",
    "https://www.coches.net/search/?arrProvince=23",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=18",
    "https://www.coches.net/search/?arrProvince=11",
    "https://www.coches.net/search/?arrProvince=45",
    "https://www.coches.net/search/?arrProvince=50",
    "https://www.coches.net/search/?arrProvince=12",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=8",
    "https://www.coches.net/search/?arrProvince=46",
    "https://www.coches.net/search/?arrProvince=33",
    "https://www.coches.net/search/?arrProvince=6",
    "https://www.coches.net/search/?arrProvince=36",
    "https://www.coches.net/search/?arrProvince=28",
    "https://www.coches.net/search/?arrProvince=41",
    "https://www.coches.net/search/?arrProvince=3",
    "https://www.coches.net/search/?arrProvince=29",
    "https://www.coches.net/search/?arrProvince=30",
    "https://www.coches.net/search/?arrProvince=32",
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
                        time.sleep(0.5)

                    except Exception as e:
                        print("Error procesando vehículo:", e)

                time.sleep(2)

    finally:
        browser.close()

print("\n🚀 Proceso completado correctamente.")
