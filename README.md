# EcoRide API

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-yellow)

API de recommandation de transport écoresponsable. À partir d'une ville et
d'une destination, EcoRide croise les conditions **météo** et l'état du
**trafic urbain** pour recommander le mode de transport optimal, avec une
estimation du temps de trajet et de l'empreinte carbone.

Version actuelle : 2.1.0

Auteur : Arthur Poncin

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Exemple d'utilisation](#exemple-dutilisation)
- [Documentation](#documentation)
- [Changelog automatisé](#changelog-automatisé)
- [Licence](#licence)

## Fonctionnalités

- **Recommandation de transport** : métro/tram, voiture électrique en
  partage, vélo électrique ou vélo standard selon les conditions
- **Météo** : fournisseur externe interrogé avec cache in-memory
  (TTL de 60 secondes) pour limiter les appels réseau
- **Trafic urbain** : récupéré en temps réel à chaque requête
- **Empreinte carbone** : estimation en grammes de CO₂ par trajet
- **Sécurité** : authentification par clé API
- **Healthcheck** : endpoint `/health` pour la supervision

## Prérequis

- Python >= 3.10
- pip

Dépendances (voir `requirements.txt`) : `fastapi`, `uvicorn`, `pydantic`.

## Installation

```bash
git clone https://github.com/ArthurPoncin/Collab.git
cd Collab

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Démarrage rapide

```bash
python main.py
```

L'API démarre sur http://localhost:8000 (Swagger UI sur `/docs`).

Vérification :

```bash
curl http://localhost:8000/health
# {"status": "healthy", "timestamp": 1718100000.0}
```

## Exemple d'utilisation

```bash
curl -X POST "http://localhost:8000/api/v1/route?token=secret_token_3a" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-42", "city": "Paris", "destination": "La Défense"}'
```

Réponse :

```json
{
  "recommended_transport": "Métro / Tram",
  "estimated_time_minutes": 35,
  "weather_condition": "Pluie",
  "carbon_footprint_g": 12.5
}
```

Sans clé API valide, l'API renvoie `401 Clé API invalide ou manquante`.

## Documentation

| Document | Description |
|----------|-------------|
| [docs/architecture.md](docs/architecture.md) | Architecture, flux de données, dépendances externes |
| [docs/api-reference.md](docs/api-reference.md) | Endpoints, paramètres, types de retour, exemples |
| [docs/installation.md](docs/installation.md) | Installation détaillée et résolution de problèmes |
| [docs/diagramme-sequence.md](docs/diagramme-sequence.md) | Diagramme de séquence du flux de recommandation |
| [CHANGELOG.md](CHANGELOG.md) | Historique des versions |

## Changelog automatisé

Le `CHANGELOG.md` est généré automatiquement à partir des messages de
commit au format Conventional Commits (`feat:`, `fix:`, ...) :

```bash
python scripts/generate_changelog.py --version 2.2.0
```

Le workflow GitHub Actions `.github/workflows/changelog.yml` le régénère
aussi à chaque tag de version `v*`.

## Licence

MIT, © 2026 Arthur Poncin
