# Guide d'installation - EcoRide API

## Prérequis

| Logiciel | Version minimale |
|----------|-----------------|
| Python | 3.10 |
| pip | 21+ |

## Installation

```bash
# Récupérer le code
git clone https://github.com/ArthurPoncin/Collab.git
cd Collab

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

Le serveur écoute sur `http://0.0.0.0:8000`.

Mode développement avec rechargement automatique :

```bash
uvicorn main:app --reload --port 8000
```

Vérification :

```bash
curl http://localhost:8000/health
# {"status": "healthy", "timestamp": 1718100000.0}
```

## Résolution de problèmes

### `ModuleNotFoundError: No module named 'fastapi'`

L'environnement virtuel n'est pas activé ou les dépendances ne sont pas
installées :

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### `Address already in use` sur le port 8000

Un autre processus occupe le port. Lancer sur un autre port :

```bash
uvicorn main:app --port 8080
```

### Réponse 401 sur /api/v1/route

La clé API est manquante ou invalide. Ajouter `?token=secret_token_3a`
à l'URL (valeur de démonstration).
