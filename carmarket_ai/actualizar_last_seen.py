from playwright.sync_api import sync_playwright
import duckdb
import datetime
import time
import sys
import random

# -------------------------
# CONFIG
# -------------------------
TARGET_DATE = "2026-02-20"

# -------------------------
# DB
# -------------------------
conn = duckdb.connect("market.db")
today = datetime.datetime.now()

cars_to_check = conn.execute("""
    SELECT url
    FROM cars
    WHERE last_seen = ?
    AND sold IS NULL
""", (TARGET_DATE,)).fetchall()

print(f"🔎 Coches a verificar: {len(cars_to_check)}")

# -------------------------
# PLAYWRIGHT
# -------------------------
with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="es-ES",
        timezone_id="Europe/Madrid"
    )

    page = context.new_page()
    page.set_default_timeout(60000)

    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """)

    # 👉 Permitir solo un bloqueo inicial
    first_url = True
    initial_block_used = False

    for (url,) in cars_to_check:

        print(f"\n➡ Comprobando: {url}")

        try:
            response = page.goto(url, wait_until="domcontentloaded")

            if response is None:
                print("🚨 Sin respuesta. Posible bloqueo.")
                browser.close()
                sys.exit()

            html = page.content().lower()

            # -------------------------
            # 🚨 BLOQUEO POR MENSAJE
            # -------------------------
            if "ups! parece que algo no va bien" in html:

                if first_url and not initial_block_used:
                    print("⚠️ Bloqueo inicial detectado. Reintentando una vez...")
                    initial_block_used = True
                    time.sleep(random.uniform(4, 7))
                    page.reload()
                    time.sleep(random.uniform(4, 7))
                    first_url = False
                    continue
                else:
                    print("🚨 BLOQUEO REAL DETECTADO. Deteniendo programa.")
                    browser.close()
                    sys.exit()

            # Ya no es primera URL
            first_url = False

            # -------------------------
            # ❌ ANUNCIO VENDIDO POR TEXTO
            # -------------------------
            if "el anuncio al que intentas acceder ya no está disponible" in html:
                print("❌ Anuncio no disponible → Marcado como vendido")

                conn.execute("""
                    UPDATE cars
                    SET sold = ?
                    WHERE url = ?
                """, (today, url))

                time.sleep(10)
                continue

            # -------------------------
            # ESPERAR JSON
            # -------------------------
            try:
                page.wait_for_function(
                    "() => window.__INITIAL_PROPS__ !== undefined",
                    timeout=10000
                )
            except:
                print("⚠️ No se encontró __INITIAL_PROPS__")
                time.sleep(10)
                continue

            data = page.evaluate("() => window.__INITIAL_PROPS__")

            if not data:
                print("⚠️ Data vacía. Saltando.")
                time.sleep(10)
                continue

            vehicle = data.get("ad")

            if not vehicle:
                print("⚠️ Sin vehículo en data. Saltando.")
                time.sleep(10)
                continue

            # -------------------------
            # ✅ ACTUALIZAR CAMPOS
            # -------------------------
            price = vehicle.get("price", 0)
            km = vehicle.get("km", 0)
            fuelType = vehicle.get("fuelType", "")
            make = vehicle.get("make", "")
            model = vehicle.get("model", "")
            title = vehicle.get("title", "")

            conn.execute("""
                UPDATE cars
                SET price = ?,
                    km = ?,
                    fuelType = ?,
                    make = ?,
                    model = ?,
                    title = ?,
                    last_seen = ?
                WHERE url = ?
            """, (
                price,
                km,
                fuelType,
                make,
                model,
                title,
                today,
                url
            ))

            print("✅ Actualizado correctamente")

        except Exception as e:
            print("🚨 Error inesperado:", e)
            browser.close()
            sys.exit()

        # -------------------------
        # ⏳ ESPERA ENTRE URLS
        # -------------------------
        time.sleep(10)

    browser.close()

print("\n🚀 Verificación terminada.")
