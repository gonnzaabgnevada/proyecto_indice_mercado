from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.coches.net/segunda-mano")
    page.wait_for_load_state("networkidle")

    # 🔥 Extraer JSON interno
    data = page.evaluate("() => window.__INITIAL_PROPS__")

    if not data:
        print("No se pudo obtener __INITIAL_PROPS__")
        browser.close()
        exit()

    # Revisar qué keys principales tiene
    print("JSON cargado. Keys principales:", data.keys())

    # Según lo que hemos visto, los vehículos pueden estar en initialResults o en initialSearch
    vehicles = []

    if "initialResults" in data:
        vehicles = data["initialResults"].get("items", [])
    elif "initialSearch" in data:
        vehicles = data["initialSearch"].get("items", [])
    
    print(f"Vehículos encontrados: {len(vehicles)}\n")

    # Mostrar un ejemplo de cada vehículo (formateado)
    for i, v in enumerate(vehicles[:5]):  # solo los primeros 5 para no saturar la consola
        print(f"Vehículo {i+1}:")
        print(json.dumps(v, indent=4, ensure_ascii=False))
        print("-" * 80)

    browser.close()
