import os
import requests, json, time, os

token = os.getenv("APIFY_API_TOKEN", "")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 38 Targeted search strings across the 16 virgin states and key gems
queries = [
    # Sonora
    "ferreteria Hermosillo Sonora",
    "refaccionaria Hermosillo Sonora",
    "carniceria cortes Hermosillo Sonora",
    "ferreteria Puerto Peñasco Sonora",
    "renta yates pesca charters Puerto Peñasco Sonora",
    "refaccionaria maquinaria Ciudad Obregón Sonora",
    "pescaderia mariscos mayoreo Guaymas Sonora",
    
    # Sinaloa
    "mariscos pescaderia mayoreo Mazatlan Sinaloa",
    "refaccionaria agricola Culiacan Sinaloa",
    "ferreteria Culiacan Sinaloa",
    "pesca deportiva charters Mazatlan Sinaloa",
    "agroinsumos semillas fertilizantes Los Mochis Sinaloa",
    "boutique ropa Culiacan Sinaloa",
    
    # Baja California Sur
    "buceo snorkel tours Cabo San Lucas BCS",
    "pesca deportiva charters Cabo San Lucas BCS",
    "licoreria vinos gourmet San Jose del Cabo BCS",
    "galeria arte boutique San Jose del Cabo BCS",
    "tours embarcaciones La Paz BCS",
    
    # Coahuila
    "ferreteria industrial Saltillo Coahuila",
    "refaccionaria camiones Torreon Coahuila",
    "materiales construccion ferreteria Monclova Coahuila",
    "refaccionaria tractocamiones Piedras Negras Coahuila",
    "carniceria cortes finos Torreon Coahuila",
    
    # Chihuahua
    "refaccionaria camiones Ciudad Juarez Chihuahua",
    "ferreteria industrial Chihuahua Chihuahua",
    "queseria lacteos mayoreo Cuauhtemoc Chihuahua",
    "talleres llanteras pesadas Ciudad Juarez Chihuahua",
    
    # Tamaulipas
    "refaccionaria traileres tractocamiones Nuevo Laredo Tamaulipas",
    "clinica dental turismo medico Reynosa Tamaulipas",
    "pescaderia mariscos Tampico Tamaulipas",
    "ferreteria mayoreo Matamoros Tamaulipas",
    
    # Michoacán
    "empaques insumos aguacate Uruapan Michoacan",
    "sistemas riego bombas agricolas Uruapan Michoacan",
    "ferreteria maquinaria Morelia Michoacan",
    
    # Colima
    "suministros navieros portuarios Manzanillo Colima",
    "refaccionaria transporte carga Manzanillo Colima",
    
    # San Luis Potosí & Aguascalientes
    "ferreteria industrial San Luis Potosi SLP",
    "refaccionaria mayoreo Aguascalientes AGS",
    "boutique blancos confeccion Aguascalientes AGS",
    
    # Nayarit
    "surf tours buceo embarcaciones Sayulita Nayarit",
    "ferreteria materiales Bahia de Banderas Nayarit"
]

print(f"Total queries prepared: {len(queries)}")

# Payload for compass/crawler-google-places
# Strictly capped at 1200 places to stay within $5 USD budget
payload = {
    "searchStringsArray": queries,
    "maxCrawledPlaces": 1200,
    "maxCrawledPlacesPerSearch": 32,
    "language": "es",
    "scrapeResponseFromOwnerText": False,
    "scrapeReviewsPersonalData": False,
    "reviewsSort": "newest",
    "maxReviews": 0,
    "maxImages": 0
}

actor_id = "compass~crawler-google-places"
url = f"https://api.apify.com/v2/acts/{actor_id}/runs"

print("Starting Apify Actor Run in the cloud...")
res = requests.post(url, headers=headers, json=payload)

if res.status_code in [200, 201]:
    run_data = res.json().get("data", {})
    run_id = run_data.get("id")
    dataset_id = run_data.get("defaultDatasetId")
    print(f"RUN STARTED SUCCESSFULLY!")
    print(f"Run ID: {run_id}")
    print(f"Dataset ID: {dataset_id}")
    print(f"Check URL: https://console.apify.com/actors/compass~crawler-google-places/runs/{run_id}")
    
    # Save run meta to disk so we can monitor or resume anytime
    meta = {
        "run_id": run_id,
        "dataset_id": dataset_id,
        "started_at": time.time(),
        "status": "RUNNING"
    }
    with open("apify_active_run.json", "w") as f:
        json.dump(meta, f)
else:
    print("Failed to start run:", res.status_code, res.text)
