# Architecture - EcoRide API

## Vue d'ensemble

EcoRide API est un service léger construit avec **FastAPI**. Il agrège
deux sources de données externes (météo, trafic) et applique une logique
métier de recommandation de transport.

```
                  ┌─────────────────────────────────┐
                  │          EcoRide API            │
                  │           (FastAPI)             │
                  │                                 │
 ┌────────┐      │  ┌──────────────────────────┐   │
 │ Client │─────>│  │ Middleware verify_api_key│   │
 └────────┘      │  └────────────┬─────────────┘   │
                  │               │                  │
                  │  ┌────────────▼─────────────┐   │      ┌──────────────────┐
                  │  │  Endpoint /api/v1/route  │──────────>│ API Météo externe │
                  │  └────────────┬─────────────┘   │      └──────────────────┘
                  │               │                  │      ┌──────────────────┐
                  │  ┌────────────▼─────────────┐   │─────>│ API Trafic urbain │
                  │  │  calculate_best_route()  │   │      └──────────────────┘
                  │  └──────────────────────────┘   │
                  │                                 │
                  │  ┌──────────────────────────┐   │
                  │  │  WEATHER_CACHE (in-mem)  │   │
                  │  │  TTL : 60 secondes       │   │
                  │  └──────────────────────────┘   │
                  └─────────────────────────────────┘
```

## Composants

### Modèles de données (Pydantic)

- `RouteRequest` : corps de la requête (`user_id`, `city`, `destination`)
- `RouteResponse` : réponse validée (`recommended_transport`,
  `estimated_time_minutes`, `weather_condition`, `carbon_footprint_g`)

### Dépendances externes

- **API Météo** (`fetch_external_weather`) : appel asynchrone vers un
  fournisseur type OpenWeatherMap (latence ~500 ms)
- **API Trafic** (`fetch_traffic_status`) : appel asynchrone vers une
  API de trafic urbain (latence ~300 ms)

### Cache météo

La météo de chaque ville est conservée en mémoire **60 secondes**
(`WEATHER_CACHE`). Au-delà, l'API externe est rappelée. Le trafic n'est
volontairement pas mis en cache : il varie trop vite.

### Sécurité

La dépendance `verify_api_key` protège l'endpoint métier : clé absente
ou invalide = `401 Unauthorized`.

## Flux de données

1. Le client appelle `POST /api/v1/route` avec sa clé API
2. La météo est lue depuis le cache, ou récupérée puis mise en cache
3. Le trafic est récupéré en temps réel
4. `calculate_best_route(météo, trafic)` détermine la recommandation :

| Météo | Trafic | Transport | Durée (min) | CO₂ (g) |
|-------|--------|-----------|-------------|---------|
| Pluie | Saturé | Métro / Tram | 35 | 12.5 |
| Pluie | Fluide | Voiture Électrique (Partage) | 20 | 45.0 |
| Autre | Saturé | Vélo Électrique | 15 | 2.0 |
| Autre | Fluide | Vélo Standard | 18 | 0.0 |

Le détail du flux est illustré dans le
[diagramme de séquence](diagramme-sequence.md).
