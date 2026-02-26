import requests
import random
import time

class Fetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/121.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
            "Connection": "keep-alive"
        })

    def get(self, url: str) -> str:
        time.sleep(random.uniform(1.5, 3.0))
        response = self.session.get(url, timeout=15)

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")

        return response.text
