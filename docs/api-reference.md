# API Reference - EcoRide API

Base URL : `http://localhost:8000`

Documentation interactive disponible sur `/docs` (Swagger UI) une fois
le serveur lancé.

## Authentification

L'endpoint `/api/v1/route` exige une clé API transmise via le paramètre
`token`. Sans clé valide : `401 Unauthorized`.

## Endpoints

### GET /health

Healthcheck du service (pas d'authentification requise).

**Réponse 200 :**

```json
{
  "status": "healthy",
  "timestamp": 1718100000.123
}
```

### POST /api/v1/route

Recommande le meilleur mode de transport selon la météo et le trafic de
la ville de départ. **Authentification requise.**

**Corps de la requête :**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `user_id` | string | oui | Identifiant de l'utilisateur |
| `city` | string | oui | Ville de départ |
| `destination` | string | oui | Destination du trajet |

**Exemple :**

```bash
curl -X POST "http://localhost:8000/api/v1/route?token=secret_token_3a" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-42", "city": "Paris", "destination": "La Défense"}'
```

**Réponse 200 :**

```json
{
  "recommended_transport": "Métro / Tram",
  "estimated_time_minutes": 35,
  "weather_condition": "Pluie",
  "carbon_footprint_g": 12.5
}
```

| Champ | Type | Description |
|-------|------|-------------|
| `recommended_transport` | string | Mode de transport recommandé |
| `estimated_time_minutes` | integer | Temps de trajet estimé en minutes |
| `weather_condition` | string | Météo utilisée (`Pluie`, `Nuageux`, `Soleil`) |
| `carbon_footprint_g` | float | Empreinte carbone estimée en grammes de CO₂ |

## Codes d'erreur

| Code | Cas | Réponse |
|------|-----|---------|
| 401 | Clé API absente ou invalide | `{"detail": "Clé API invalide ou manquante"}` |
| 422 | Corps de requête invalide | Détail de validation Pydantic |
| 503 | Fournisseur météo injoignable | `{"detail": "Service météo indisponible"}` |
