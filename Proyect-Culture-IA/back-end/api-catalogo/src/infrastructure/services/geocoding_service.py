import requests

def get_coordinates_from_nominatim(address: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "co",
    }
    response = requests.get(url, params=params, headers={"User-Agent": "api-catalogo/1.0"})
    response.raise_for_status()
    data = response.json()
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None, None
