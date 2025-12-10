# 🚀 GUIDE DE DÉMARRAGE RAPIDE

## Avant de Commencer

### ✅ Vérifications
- [ ] Docker Desktop installé et lancé
- [ ] Python 3.8+ installé
- [ ] Terminal PowerShell ouvert dans le dossier `NoSQL`

---

## 📦 Installation (5 minutes)

### Étape 1: Installer les dépendances Python
```powershell
pip install -r requirements.txt
```

**Attendu**: Installation de redis, pymongo, faker, colorama, tabulate

### Étape 2: Lancer Redis et MongoDB avec Docker
```powershell
docker-compose up -d
```

**Attendu**: 
```
✔ Container delivery-redis    Started
✔ Container delivery-mongodb  Started
```

### Étape 3: Vérifier que les services sont actifs
```powershell
docker-compose ps
```

**Attendu**: Les deux conteneurs doivent être "Up"

---

## 🎮 Exécution du Projet

### Option A: Menu Interactif (Recommandé)
```powershell
python main_demo.py
```

**Ce que vous verrez**:
```
================================================================================
            PROJET NOSQL - SYSTÈME DE GESTION DE LIVRAISONS
================================================================================

MENU PRINCIPAL
────────────────────────────────────────────────────────────────────────────

1. Partie 1 - État temps réel avec Redis
2. Partie 2 - Historique et analyses avec MongoDB
3. Partie 3 - Structures avancées
4. Partie 4 - Geo-spatial (localisation temps réel)
5. Exécuter TOUTES les parties
6. Tester les connexions
0. Quitter

Votre choix: 
```

**Que choisir?**
- **Première fois**: Choisissez `6` pour tester les connexions
- **Démonstration complète**: Choisissez `5` pour tout exécuter
- **Partie spécifique**: Choisissez `1`, `2`, `3`, ou `4`

### Option B: Exécuter une partie spécifique
```powershell
# Partie 1 uniquement
python partie1_redis_temps_reel.py

# Partie 2 uniquement
python partie2_mongodb_historique.py

# Partie 3 uniquement
python partie3_avancees.py

# Partie 4 uniquement
python partie4_geospatial.py
```

---

## 📊 Ce que fait chaque partie

### Partie 1: Redis Temps Réel
- ✅ Initialise 24 livreurs avec ratings
- ✅ Crée 34 commandes avec différents statuts
- ✅ Démontre l'affectation atomique (script Lua)
- ✅ Affiche un dashboard temps réel

**Durée**: ~2 minutes (avec pauses)

### Partie 2: MongoDB Historique
- ✅ Importe 154 livraisons dans MongoDB
- ✅ Requête historique d'un livreur
- ✅ Agrégation par région
- ✅ Top 2 livreurs par revenu
- ✅ Création d'index stratégiques

**Durée**: ~2 minutes

### Partie 3: Structures Avancées
- ✅ Configuration multi-régions
- ✅ Cache avec expiration (TTL 30s)
- ✅ Fonction de rafraîchissement

**Durée**: ~1 minute

### Partie 4: Geo-spatial
- ✅ Stockage de 10 lieux + 4 livreurs GPS
- ✅ Recherche livreurs dans rayon de 2km
- ✅ Affectation optimale (3 stratégies)
- ✅ Simulation monitoring temps réel

**Durée**: ~3 minutes

**Total si tout exécuté**: ~8 minutes

---

## 🔧 Commandes Utiles

### Docker

```powershell
# Voir les logs Redis
docker-compose logs redis

# Voir les logs MongoDB
docker-compose logs mongodb

# Redémarrer les services
docker-compose restart

# Arrêter les services
docker-compose down

# Arrêter ET supprimer les données
docker-compose down -v
```

### Accès Direct aux Bases

```powershell
# Shell Redis
docker exec -it delivery-redis redis-cli

# Dans Redis CLI, essayez:
# KEYS *
# HGETALL driver:d1
# ZRANGE drivers:ratings 0 -1 WITHSCORES

# Shell MongoDB
docker exec -it delivery-mongodb mongosh -u admin -p admin123

# Dans MongoDB shell, essayez:
# use delivery
# db.deliveries.find().limit(5)
# db.deliveries.countDocuments()
```

---

## ❌ Dépannage

### Problème: "Connexion Redis refusée"

**Solution 1**: Vérifier que Docker tourne
```powershell
docker ps
```

**Solution 2**: Redémarrer Redis
```powershell
docker-compose restart redis
```

**Solution 3**: Vérifier les logs
```powershell
docker-compose logs redis
```

### Problème: "Connexion MongoDB échouée"

**Solution 1**: Attendre que MongoDB démarre complètement (~10 secondes)
```powershell
docker-compose logs mongodb | Select-String "Waiting for connections"
```

**Solution 2**: Redémarrer MongoDB
```powershell
docker-compose restart mongodb
```

### Problème: "Module 'redis' not found"

**Solution**: Réinstaller les dépendances
```powershell
pip install -r requirements.txt --force-reinstall
```

### Problème: Port déjà utilisé (6379 ou 27017)

**Solution**: Arrêter le processus qui utilise le port OU modifier le port dans `docker-compose.yml`
```powershell
# Trouver le processus sur le port 6379
netstat -ano | findstr :6379

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F
```

---

## 📚 Documentation

### Pour démarrer rapidement
👉 **README.md** - Ce fichier que vous lisez

### Pour comprendre l'implémentation
👉 **DOCUMENTATION.md** - 600+ lignes d'explications techniques
- Architecture détaillée
- Justification des choix
- Résultats de chaque travail
- Guide complet

### Pour voir les livrables
👉 **walkthrough.md** - Résumé du projet complet
- Vue d'ensemble
- Tests et validation
- Performances mesurées

---

## 🎯 Checklist de Livraison

Avant de rendre le projet, vérifiez:

- [ ] Docker Compose fonctionne (`docker-compose up -d`)
- [ ] Connexions testées (option 6 du menu)
- [ ] Au moins une partie exécutée sans erreur
- [ ] README.md lu
- [ ] DOCUMENTATION.md consultée
- [ ] Tous les fichiers présents (15 fichiers)

### Fichiers à rendre:
```
✅ docker-compose.yml
✅ requirements.txt
✅ .env
✅ utils.py
✅ data_generator.py
✅ partie1_redis_temps_reel.py
✅ partie2_mongodb_historique.py
✅ partie3_avancees.py
✅ partie4_geospatial.py
✅ main_demo.py
✅ README.md
✅ DOCUMENTATION.md
```

---

## 💡 Astuces

### Pour une démonstration rapide
```powershell
python main_demo.py
# Puis choisir: 5 (Exécuter tout)
# Appuyez sur Entrée à chaque pause
```

### Pour explorer Redis manuellement
```powershell
docker exec -it delivery-redis redis-cli
> KEYS driver:*
> HGETALL driver:d1
> ZRANGE drivers:ratings 0 -1 WITHSCORES
```

### Pour explorer MongoDB manuellement
```powershell
docker exec -it delivery-mongodb mongosh -u admin -p admin123
> use delivery
> db.deliveries.find().pretty().limit(1)
> db.deliveries.aggregate([{$group: {_id: "$region", count: {$sum: 1}}}])
```

---

## 🎉 Prêt à Commencer!

```powershell
# 1. Installer
pip install -r requirements.txt

# 2. Lancer
docker-compose up -d

# 3. Exécuter
python main_demo.py
```

**Bon projet! 🚀**
