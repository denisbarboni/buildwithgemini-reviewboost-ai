"""External Public API integrations for ReviewBoost AI.
Uses free, keyless public APIs:
- QRServer API (https://api.qrserver.com) for QR Code generation.
- OpenStreetMap Nominatim API (https://nominatim.openstreetmap.org) for business location lookup.
"""
import urllib.parse
import urllib.request
import json



def generate_qr_code_url(review_link: str, size: str = "250x250") -> str:
    """Generates a public QR Code image URL for a Google review link using the free QRServer Public API.

    Args:
        review_link: The URL destination for customer reviews (e.g. 'https://g.page/r/bellavista/review').
        size: Image size in pixels (e.g. '250x250').

    Returns:
        A text message containing the direct image URL for the generated QR Code.
    """
    encoded_link = urllib.parse.quote(review_link, safe="")
    qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size={size}&data={encoded_link}"
    return f"QR Code gerado com sucesso! Imagem disponível em: {qr_image_url}"


def search_local_business_address(business_name: str, city: str = "") -> str:
    """Searches for a local business address and geographic location using OpenStreetMap Nominatim API.

    Args:
        business_name: Name of the business (e.g., 'Padaria Bella Vista').
        city: Optional city name (e.g., 'São Paulo').

    Returns:
        Formatted location details or search status.
    """
    query = f"{business_name} {city}".strip()
    encoded_query = urllib.parse.quote(query)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&limit=1"

    req = urllib.request.Request(url, headers={"User-Agent": "ReviewBoostAI/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                if data:
                    res = data[0]
                    display_name = res.get("display_name", "Local encontrado")
                    lat = res.get("lat", "")
                    lon = res.get("lon", "")
                    return f"Endereço localizado: {display_name} (Lat: {lat}, Lon: {lon})"
                return f"Nenhum endereço encontrado para '{query}' no OpenStreetMap."
    except Exception as e:
        return f"Erro ao consultar serviço de localização: {str(e)}"
    return f"Nenhum endereço encontrado para '{query}'."
