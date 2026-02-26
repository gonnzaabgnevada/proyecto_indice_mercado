import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36"
}

r = requests.get("https://www.coches.net/", headers=headers)

print(r.status_code)
print("Ups!" in r.text)
