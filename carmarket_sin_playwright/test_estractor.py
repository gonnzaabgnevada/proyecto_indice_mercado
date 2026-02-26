from fetcher import Fetcher
from extractor import extract_vehicle_data

url = "https://www.coches.net/dacia-sandero-stepway-extreme-go-tce-81kw-110cv-5p-gasolina-2022-en-granada-62655965-covo.aspx"

fetcher = Fetcher()
html = fetcher.get(url)

vehicle = extract_vehicle_data(html)

print("Precio:", vehicle["price"])
print("KM:", vehicle["km"])
print("Marca:", vehicle["make"])
print("Modelo:", vehicle["model"])
