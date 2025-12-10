# Système de Gestion de Livraisons NoSQL

Projet complet de gestion de livraisons utilisant **Redis** pour l'état temps réel et **MongoDB** pour l'historique et les analyses.

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.8+
- Docker et Docker Compose
- Git (optionnel)

### Installation

1. **Cloner ou télécharger le projet**
```bash
cd NoSQL
```

2. **Installer les dépendances Python**
```bash
pip install -r requirements.txt
```

3. **Lancer les services Docker (Redis + MongoDB)**
```bash
docker-compose up -d
```

4. **Vérifier que les services sont actifs**
```bash
docker-compose ps
```

### Exécution

**Option 1: Menu interactif (recommandé)**
```bash
python main_demo.py
```

**Option 2: Exécuter une partie spécifique**
```bash
python partie1_redis_temps_reel.py
python partie2_mongodb_historique.py
python partie3_avancees.py
python partie4_geospatial.py
```

## 📁 Structure du Projet

```
NoSQL/
├── docker-compose.yml           # Configuration Docker
├── requirements.txt             # Dépendances Python
├── .env                         # Variables d'environnement
├── utils.py                     # Fonctions utilitaires
├── data_generator.py            # Générateur de données
├── partie1_redis_temps_reel.py  # Partie 1: Redis
├── partie2_mongodb_historique.py# Partie 2: MongoDB
├── partie3_avancees.py          # Partie 3: Avancé
├── partie4_geospatial.py        # Partie 4: Geo-spatial
├── main_demo.py                 # Script principal
├── DOCUMENTATION.md             # Documentation complète
└── README.md                    # Ce fichier
```

## 📋 Contenu du Projet

### Partie 1: État Temps Réel (Redis)
- Gestion des livreurs avec différentes structures Redis
- Commandes en cours avec statuts
- Affectation atomique avec scripts Lua
- Dashboard temps réel

### Partie 2: Historique et Analyses (MongoDB)
- Import d'historique de livraisons
- Requêtes et agrégations MongoDB
- Indexation stratégique
- Synchronisation Redis → MongoDB

### Partie 3: Structures Avancées
- Livreurs multi-régions
- Cache avec TTL (expiration automatique)

### Partie 4: Geo-spatial
- Stockage de positions GPS
- Recherche de livreurs proches
- Affectation optimale basée sur distance/rating
- Monitoring temps réel

## 🔧 Commandes Utiles

### Docker
```bash
# Démarrer les services
docker-compose up -d

# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs

# Accéder au shell Redis
docker exec -it delivery-redis redis-cli

# Accéder au shell MongoDB
docker exec -it delivery-mongodb mongosh -u admin -p admin123
```

### Python
```bash
# Tester les connexions
python -c "from utils import *; get_redis_connection(); get_mongodb_connection()"

# Générer des données de test
python data_generator.py
```

## 📖 Documentation

Pour plus de détails sur l'implémentation, les choix techniques et les résultats, consultez [DOCUMENTATION.md](DOCUMENTATION.md).

## 🎯 Critères de Réussite

✓ Toutes les requêtes Redis et MongoDB s'exécutent sans erreur  
✓ Les résultats correspondent au comportement attendu  
✓ Les explications justifient les choix  
✓ Le document est bien structuré et lisible  
✓ Bonus: idées créatives et optimisations

## 📝 Notes

- Les données sont générées automatiquement avec des valeurs réalistes
- Les scripts sont commentés et structurés pour faciliter la compréhension
- La mise en route est documentée étape par étape
- Tous les travaux demandés sont implémentés avec des bonus

## 👥 Auteur

Projet réalisé dans le cadre du cours NoSQL.
