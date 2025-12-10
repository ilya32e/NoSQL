"""
PARTIE 2 : Historique et Analyses avec MongoDB

Ce script implémente tous les travaux de la Partie 2:
- Travail 1: Importer l'historique
- Travail 2: Requête simple - historique d'un livreur
- Travail 3: Agrégation - performance par région
- Travail 4: Agrégation avancée - top livreurs
- Travail 5: Gestion des données (indexation)
- Travail 6: Synchronisation Redis → MongoDB
"""

from datetime import datetime, timedelta
from utils import *
from data_generator import DataGenerator


class MongoDeliveryHistory:
    """Système de gestion d'historique de livraisons avec MongoDB"""
    
    def __init__(self, db):
        self.db = db
        self.deliveries = db['deliveries']
    
    # =====================================================================
    # TRAVAIL 1 : Importer l'historique
    # =====================================================================
    
    def import_deliveries(self, deliveries_data):
        """
        Importer l'historique des livraisons dans MongoDB
        Structure de document:
        {
            command_id, client, driver_id, driver_name,
            pickup_time, delivery_time, duration_minutes,
            amount, region, rating, review, status
        }
        """
        print_subheader("TRAVAIL 1 : Import de l'historique des livraisons")
        
        # Nettoyer la collection
        self.deliveries.delete_many({})
        
        # Insérer les livraisons
        if deliveries_data:
            result = self.deliveries.insert_many(deliveries_data)
            print_success(f"{len(result.inserted_ids)} livraisons importées dans MongoDB")
        
        # Afficher un exemple
        sample = self.deliveries.find_one()
        if sample:
            print_info("Exemple de document:")
            print(f"  Command ID: {sample.get('command_id')}")
            print(f"  Client: {sample.get('client')}")
            print(f"  Driver: {sample.get('driver_name')} ({sample.get('driver_id')})")
            print(f"  Durée: {sample.get('duration_minutes')} minutes")
            print(f"  Montant: {sample.get('amount')}€")
            print(f"  Région: {sample.get('region')}")
            print(f"  Rating: {sample.get('rating')}")
            print(f"  Avis: {sample.get('review')}")
    
    # =====================================================================
    # TRAVAIL 2 : Requête simple - Historique d'un livreur
    # =====================================================================
    
    def get_driver_history(self, driver_id):
        """
        Afficher toutes les livraisons d'un livreur
        + leur nombre + le montant total
        """
        print_subheader(f"TRAVAIL 2 : Historique du livreur {driver_id}")
        
        # Requête simple: filtrer par driver_id
        deliveries = list(self.deliveries.find({'driver_id': driver_id}))
        
        if not deliveries:
            print_warning(f"Aucune livraison trouvée pour {driver_id}")
            return
        
        # Afficher les livraisons
        delivery_data = []
        total_amount = 0
        for d in deliveries:
            delivery_data.append([
                d['command_id'],
                d['client'],
                d['destination'],
                f"{d['amount']}€",
                f"{d['duration_minutes']}min",
                d['rating']
            ])
            total_amount += d['amount']
        
        print_table(
            ['Commande', 'Client', 'Destination', 'Montant', 'Durée', 'Rating'],
            delivery_data,
            f"Livraisons de {driver_id}"
        )
        
        print_success(f"Nombre de livraisons: {len(deliveries)}")
        print_success(f"Montant total: {total_amount}€")
    
    # =====================================================================
    # TRAVAIL 3 : Agrégation - Performance par région
    # =====================================================================
    
    def analyze_by_region(self):
        """
        Agrégation par région:
        - Nombre de livraisons
        - Revenu total
        - Durée moyenne
        - Rating moyen
        Trié par revenu décroissant
        """
        print_subheader("TRAVAIL 3 : Performance par région")
        
        pipeline = [
            # Grouper par région
            {
                '$group': {
                    '_id': '$region',
                    'nombre_livraisons': {'$sum': 1},
                    'revenu_total': {'$sum': '$amount'},
                    'duree_moyenne': {'$avg': '$duration_minutes'},
                    'rating_moyen': {'$avg': '$rating'}
                }
            },
            # Trier par revenu décroissant
            {
                '$sort': {'revenu_total': -1}
            }
        ]
        
        results = list(self.deliveries.aggregate(pipeline))
        
        if results:
            region_data = []
            for r in results:
                region_data.append([
                    r['_id'],
                    r['nombre_livraisons'],
                    f"{r['revenu_total']}€",
                    f"{r['duree_moyenne']:.1f}min",
                    f"{r['rating_moyen']:.2f}"
                ])
            
            print_table(
                ['Région', 'Livraisons', 'Revenu Total', 'Durée Moy.', 'Rating Moy.'],
                region_data,
                "Performance par région"
            )
        else:
            print_warning("Aucune donnée trouvée")
    
    # =====================================================================
    # TRAVAIL 4 : Agrégation avancée - Top livreurs
    # =====================================================================
    
    def get_top_drivers(self, limit=2):
        """
        Agrégation avancée:
        1. Grouper par livreur
        2. Calculer nombre de livraisons, revenu total, durée moyenne, rating moyen
        3. Trier par revenu décroissant
        4. Retourner le top N
        """
        print_subheader(f"TRAVAIL 4 : Top {limit} livreurs")
        
        pipeline = [
            # Grouper par livreur
            {
                '$group': {
                    '_id': '$driver_id',
                    'driver_name': {'$first': '$driver_name'},
                    'nombre_livraisons': {'$sum': 1},
                    'revenu_total': {'$sum': '$amount'},
                    'duree_moyenne': {'$avg': '$duration_minutes'},
                    'rating_moyen': {'$avg': '$rating'}
                }
            },
            # Trier par revenu décroissant
            {
                '$sort': {'revenu_total': -1}
            },
            # Limiter aux N premiers
            {
                '$limit': limit
            }
        ]
        
        results = list(self.deliveries.aggregate(pipeline))
        
        if results:
            driver_data = []
            for r in results:
                driver_data.append([
                    r['_id'],
                    r['driver_name'],
                    r['nombre_livraisons'],
                    f"{r['revenu_total']}€",
                    f"{r['duree_moyenne']:.1f}min",
                    f"{r['rating_moyen']:.2f}"
                ])
            
            print_table(
                ['ID', 'Nom', 'Livraisons', 'Revenu Total', 'Durée Moy.', 'Rating Moy.'],
                driver_data,
                f"Top {limit} livreurs par revenu"
            )
        else:
            print_warning("Aucune donnée trouvée")
    
    # =====================================================================
    # TRAVAIL 5 : Gestion des données (Indexation)
    # =====================================================================
    
    def create_indexes(self):
        """
        Créer des index stratégiques:
        - Index sur driver_id pour requêtes par livreur
        - Index composé sur region + delivery_time pour analyses régionales
        """
        print_subheader("TRAVAIL 5 : Création d'index stratégiques")
        
        # Index simple sur driver_id
        try:
            self.deliveries.create_index('driver_id', name='idx_driver_id')
            print_success("Index créé sur 'driver_id'")
        except Exception as e:
            print_info(f"Index 'driver_id' existe déjà ou erreur: {str(e)[:50]}")
        print_info("  → Optimise les requêtes filtrant par livreur (Travail 2)")
        print_info("  → Améliore les performances des agrégations par livreur")
        
        # Index composé sur region + delivery_time
        try:
            self.deliveries.create_index(
                [('region', 1), ('delivery_time', -1)],
                name='idx_region_delivery_time'
            )
            print_success("Index composé créé sur 'region' + 'delivery_time'")
        except Exception as e:
            print_info(f"Index composé existe déjà ou erreur: {str(e)[:50]}")
        print_info("  → Optimise les analyses par région avec tri temporel")
        print_info("  → Permet des requêtes rapides sur les livraisons récentes d'une région")
        
        # Index sur command_id pour recherches rapides (non unique si doublons possibles)
        try:
            self.deliveries.create_index('command_id', name='idx_command_id')
            print_success("Index créé sur 'command_id'")
        except Exception as e:
            print_info(f"Index 'command_id' existe déjà ou erreur: {str(e)[:50]}")
        print_info("  → Accélère les recherches par ID de commande")
        
        # Afficher tous les index
        print("\n--- Index de la collection 'deliveries' ---")
        indexes = self.deliveries.list_indexes()
        for idx in indexes:
            print(f"  • {idx['name']}: {idx['key']}")
    
    
    # =====================================================================
    # TRAVAIL 6 : Synchronisation Redis → MongoDB
    # =====================================================================
    
    def sync_from_redis(self, redis_conn, order_id):
        """
        Synchroniser une livraison terminée depuis Redis vers MongoDB
        Cette fonction est appelée quand une livraison est marquée comme "livrée"
        """
        print_subheader(f"TRAVAIL 6 : Synchronisation de {order_id} vers MongoDB")
        
        # Récupérer les infos de la commande depuis Redis
        order_key = f"order:{order_id}"
        order_info = redis_conn.hgetall(order_key)
        
        if not order_info or order_info.get('status') != 'livrée':
            print_error(f"Commande {order_id} non trouvée ou pas encore livrée")
            return False
        
        # Récupérer le livreur
        driver_id = redis_conn.get(f"assignment:{order_id}")
        if not driver_id:
            print_error(f"Pas d'affectation trouvée pour {order_id}")
            return False
        
        driver_info = redis_conn.hgetall(f"driver:{driver_id}")
        
        # Créer le document MongoDB
        delivery_doc = {
            'command_id': order_id,
            'client': order_info.get('client'),
            'driver_id': driver_id,
            'driver_name': driver_info.get('name'),
            'pickup_time': datetime.fromisoformat(order_info.get('created_at')),
            'delivery_time': datetime.now(),  # Temps actuel
            'duration_minutes': 20,  # Valeur par défaut ou calculée
            'amount': float(order_info.get('amount')),
            'region': driver_info.get('region'),
            'rating': float(driver_info.get('rating')),
            'review': 'Livraison synchronisée depuis Redis',
            'status': 'completed',
            'destination': order_info.get('destination'),
        }
        
        # Insérer ou mettre à jour dans MongoDB
        self.deliveries.update_one(
            {'command_id': order_id},
            {'$set': delivery_doc},
            upsert=True
        )
        
        print_success(f"Livraison {order_id} synchronisée dans MongoDB")
        print_info(f"  Driver: {driver_info.get('name')} ({driver_id})")
        print_info(f"  Montant: {order_info.get('amount')}€")
        
        return True


def create_initial_deliveries():
    """Créer les 4 livraisons initiales du projet"""
    base_time = datetime(2025, 12, 6, 14, 0)
    
    deliveries = [
        {
            'command_id': 'c1',
            'client': 'Client A',
            'driver_id': 'd3',
            'driver_name': 'Charlie Lefevre',
            'pickup_time': base_time + timedelta(minutes=5),
            'delivery_time': base_time + timedelta(minutes=25),
            'duration_minutes': 20,
            'amount': 25,
            'region': 'Paris',
            'rating': 4.9,
            'review': 'Excellent service!',
            'status': 'completed',
            'destination': 'Marais',
        },
        {
            'command_id': 'c2',
            'client': 'Client B',
            'driver_id': 'd1',
            'driver_name': 'Alice Dupont',
            'pickup_time': base_time + timedelta(minutes=10),
            'delivery_time': base_time + timedelta(minutes=25),
            'duration_minutes': 15,
            'amount': 15,
            'region': 'Paris',
            'rating': 4.8,
            'review': 'Très professionnel',
            'status': 'completed',
            'destination': 'Belleville',
        },
        {
            'command_id': 'c3',
            'client': 'Client C',
            'driver_id': 'd2',
            'driver_name': 'Bob Martin',
            'pickup_time': base_time + timedelta(minutes=15),
            'delivery_time': base_time + timedelta(minutes=40),
            'duration_minutes': 25,
            'amount': 30,
            'region': 'Paris',
            'rating': 4.5,
            'review': 'Livraison rapide, merci!',
            'status': 'completed',
            'destination': 'Bercy',
        },
        {
            'command_id': 'c4',
            'client': 'Client D',
            'driver_id': 'd1',
            'driver_name': 'Alice Dupont',
            'pickup_time': base_time + timedelta(minutes=20),
            'delivery_time': base_time + timedelta(minutes=38),
            'duration_minutes': 18,
            'amount': 20,
            'region': 'Paris',
            'rating': 4.8,
            'review': 'Parfait comme toujours',
            'status': 'completed',
            'destination': 'Auteuil',
        },
    ]
    
    return deliveries


def run_partie2():
    """Exécuter tous les travaux de la Partie 2"""
    
    print_header("PARTIE 2 : HISTORIQUE ET ANALYSES AVEC MONGODB")
    
    # Connexion MongoDB
    db = get_mongodb_connection()
    if db is None:
        print_error("Impossible de se connecter à MongoDB. Assurez-vous que Docker est lancé.")
        return
    
    # Initialiser le système
    history = MongoDeliveryHistory(db)
    
    # Générer des données
    initial_deliveries = create_initial_deliveries()
    drivers = DataGenerator.get_initial_drivers() + DataGenerator.generate_drivers(15)
    orders = DataGenerator.get_initial_orders() + DataGenerator.generate_orders(50)
    additional_deliveries = DataGenerator.generate_deliveries(drivers, orders, 150)
    
    all_deliveries = initial_deliveries + additional_deliveries
    
    # TRAVAIL 1 : Importer l'historique
    history.import_deliveries(all_deliveries)
    wait_for_input()
    
    # TRAVAIL 2 : Historique d'un livreur
    history.get_driver_history('d1')
    wait_for_input()
    
    # TRAVAIL 3 : Performance par région
    history.analyze_by_region()
    wait_for_input()
    
    # TRAVAIL 4 : Top livreurs
    history.get_top_drivers(2)
    wait_for_input()
    
    # TRAVAIL 5 : Créer les index
    history.create_indexes()
    wait_for_input()
    
    # TRAVAIL 6 : Exemple de synchronisation Redis → MongoDB
    print_subheader("TRAVAIL 6 : Synchronisation Redis → MongoDB")
    print_info("Cette fonctionnalité permet de synchroniser automatiquement")
    print_info("les livraisons terminées depuis Redis vers MongoDB.")
    print_info("Fonction: sync_from_redis(redis_conn, order_id)")
    print_info("Appelée automatiquement lors de la complétion d'une livraison.")
    
    # Démonstration avec connexion Redis
    r = get_redis_connection()
    if r:
        # Chercher une commande livrée
        delivered_orders = r.smembers('orders:status:livrée')
        if delivered_orders:
            sample_order = list(delivered_orders)[0]
            print_info(f"\nDémonstration avec la commande {sample_order}:")
            history.sync_from_redis(r, sample_order)
    
    print_success("\n✓ Partie 2 terminée avec succès!")


if __name__ == "__main__":
    from datetime import timedelta
    run_partie2()
