import asyncio
import time
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI(title="EcoRide API", version="2.1.0")

# --- SIMULATION DE BASE DE DONNÉES / CACHE IN-MEMORY ---
# Structure : { "ville": {"data": ..., "timestamp": ...} }
WEATHER_CACHE: Dict[str, dict] = {}
CACHE_TTL = 60  # Le cache expire après 60 secondes


# --- MODÈLES DE DONNÉES ---
class RouteRequest(BaseModel):
    user_id: str
    city: str
    destination: str


class RouteResponse(BaseModel):
    recommended_transport: str
    estimated_time_minutes: int
    weather_condition: str
    carbon_footprint_g: float


# --- SERVICES EXTERNES (SIMULÉS) ---
async def fetch_external_weather(city: str) -> str:
    """Simule un appel HTTP vers un fournisseur météo externe (ex: OpenWeatherMap)"""
    await asyncio.sleep(0.5)  # Simule la latence réseau
    city_lower = city.lower()
    if "paris" in city_lower:
        return "Pluie"
    if "lyon" in city_lower:
        return "Nuageux"
    return "Soleil"


async def fetch_traffic_status(city: str) -> str:
    """Simule un appel vers une API de trafic urbain"""
    await asyncio.sleep(0.3)
    if "paris" in city.lower():
        return "Saturé"
    return "Fluide"


# --- LOGIQUE MÉTIER ---
def calculate_best_route(weather: str, traffic: str) -> tuple[str, int, float]:
    """Détermine le meilleur transport selon la météo et le trafic"""
    if weather == "Pluie":
        if traffic == "Saturé":
            return "Métro / Tram", 35, 12.5
        return "Voiture Électrique (Partage)", 20, 45.0
    
    if traffic == "Saturé":
        return "Vélo Électrique", 15, 2.0
        
    return "Vélo Standard", 18, 0.0


# --- MIDDLEWARE DE SÉCURITÉ (Ajouté en V2.0.0) ---
def verify_api_key(api_key: Optional[str] = None):
    # En production, cela vérifierait une vraie base de données
    if not api_key or api_key != "secret_token_3a":
        raise HTTPException(status_code=401, detail="Clé API invalide ou manquante")
    return api_key


# --- ENDPOINTS ---
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}


@app.post("/api/v1/route", response_model=RouteResponse)
async def get_recommendation(request: RouteRequest, token: str = Depends(verify_api_key)):
    city = request.city
    current_time = time.time()
    
    # 1. Gestion du Cache Météo
    if city in WEATHER_CACHE and (current_time - WEATHER_CACHE[city]["timestamp"]) < CACHE_TTL:
        weather = WEATHER_CACHE[city]["data"]
        cached_used = True
    else:
        try:
            weather = await fetch_external_weather(city)
            WEATHER_CACHE[city] = {"data": weather, "timestamp": current_time}
            cached_used = False
        except Exception:
            raise HTTPException(status_code=503, detail="Service météo indisponible")

    # 2. Récupération du trafic (Non caché, varie trop vite)
    traffic = await fetch_traffic_status(city)
    
    # 3. Calcul de la recommandation
    transport, duration, co2 = calculate_best_route(weather, traffic)
    
    return RouteResponse(
        recommended_transport=transport,
        estimated_time_minutes=duration,
        weather_condition=weather,
        carbon_footprint_g=co2
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)