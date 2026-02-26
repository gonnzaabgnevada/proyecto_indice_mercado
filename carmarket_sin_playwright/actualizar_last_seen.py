import requests
import duckdb
import datetime
import time
import random
import re
import json
import sys

# -------------------------
# CONFIG
# -------------------------
TARGET_DATE = "2026-02-20"
DB_PATH = r"C:\Users\crest\Desktop\proyecto_indice_mercado\carmarket_ai\market.db"

BASE_URL = "https://www.coches.net"
BLOCK_TEXT = "ups! parece que algo no va bien"
SOLD_TEXT = "el anuncio al que intentas acceder ya no está disponible"

MAX_RETRIES = 3

# -------------------------
# SESSION SETUP
# -------------------------
session = requests.Session()

session.headers.update({
    "User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    ]),
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Connection": "keep-alive"
})

# -------------------------
# DB
# -------------------------
conn = duckdb.connect(DB_PATH)
today = datetime.datetime.now()

cars_to_check = conn.execute("""
    SELECT url
    FROM cars
    WHERE last_seen = ?
    AND sold IS NULL
""", (TARGET_DATE,)).fetchall()

print(f"🔎 Coches a verificar: {len(cars_to_check)}")

# -------------------------
# WARMUP (IMPORTANTÍSIMO)
# -------------------------
print("🔥 Warmup inicial...")
try:
    session.get(BASE_URL, timeout=15)
    time.sleep(random.uniform(2, 4))
except:
    print("⚠️ Falló warmup inicial")

# -------------------------
# FUNCIONES
# -------------------------

def human_delay():
    time.sleep(random.uniform(8, 15))


def fetch_with_retry(url):
    backoff = 5

    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(
                url,
                headers={
                    "Referer": "https://www.coches.net/segunda-mano/"
                },
                timeout=20
            )

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")

            html = response.text.lower()

            if BLOCK_TEXT in html:
                print(f"🚨 Bloqueo detectado (intento {attempt+1})")
                time.sleep(backoff)
                backoff *= 2
                continue

            return response.text

        except Exception as e:
            print(f"⚠️ Error intento {attempt+1}: {e}")
            time.sleep(backoff)
            backoff *= 2

    return None


def extract_json(html):
    match = re.search(r'window\.__INITIAL_PROPS__\s*=\s*JSON\.parse\("(.*?)"\);', html)
    if not match:
        return None

    try:
        json_string = match.group(1)
        json_string = json_string.encode().decode('unicode_escape')
        return json.loads(json_string)
    except:
        return None


# -------------------------
# MAIN LOOP
# -------------------------

for (url,) in cars_to_check:

    print(f"\n➡ Comprobando: {url}")

    html = fetch_with_retry(url)

    if html is None:
        print("🚨 Demasiados bloqueos. Deteniendo programa por seguridad.")
        sys.exit()

    lower_html = html.lower()

    # -------------------------
    # ❌ ANUNCIO VENDIDO
    # -------------------------
    if SOLD_TEXT in lower_html:
        print("❌ Anuncio no disponible → Marcado como vendido")

        conn.execute("""
            UPDATE cars
            SET sold = ?
            WHERE url = ?
        """, (today, url))

        human_delay()
        continue

    # -------------------------
    # EXTRAER JSON
    # -------------------------
    data = extract_json(html)

    if not data:
        print("⚠️ No se pudo extraer JSON. Saltando sin marcar vendido.")
        human_delay()
        continue

    vehicle = data.get("ad")

    if not vehicle:
        print("⚠️ Sin vehículo en JSON. Saltando.")
        human_delay()
        continue

    # -------------------------
    # ACTUALIZAR
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

    human_delay()

print("\n🚀 Verificación terminada.")
