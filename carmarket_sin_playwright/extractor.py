import re
import json

def extract_vehicle_data(html: str) -> dict:

    pattern = r'window\.__INITIAL_PROPS__\s*=\s*JSON\.parse\("(.+?)"\);'
    match = re.search(pattern, html)

    if not match:
        raise Exception("No se encontró __INITIAL_PROPS__")

    json_escaped = match.group(1)

    # Desescapar string JSON
    json_string = bytes(json_escaped, "utf-8").decode("unicode_escape")

    data = json.loads(json_string)

    return data.get("ad")
