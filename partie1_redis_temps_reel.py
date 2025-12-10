"""
PARTIE 1 : État temps réel avec Redis (Livreurs et Commandes)

Ce script implémente tous les travaux de la Partie 1:
- Travail 1: Initialiser les livreurs
- Travail 2: Gérer les commandes en cours
- Travail 3: Affecter une commande à un livreur (atomique)
- Travail 4: Commandes affectées vs en attente
- Travail 5: Simulation d'une livraison
- Travail 6: État global du système (dashboard)
"""

import json
from utils import *
from data_generator import DataGenerator


class RedisDeliverySystem:
    """Système de gestion de livraisons temps réel avec Redis"""
    
    def __init__(self, redis_conn):
        self.r = redis_conn
    
    # =====================================================================
    # TRAVAIL 1 : Initialiser les livreurs
    # =====================================================================
    
    def initialize_drivers(self, drivers):
        """
        Initialiser les livreurs dans Redis avec plusieurs structures:
        - driver:{id} : Hash contenant toutes les infos du livreur
        - drivers:ratings : Sorted Set pour accès rapide par rating
        - drivers:all : Set contenant tous les IDs de livreurs
        """
        print_subheader("TRAVAIL 1 : Initialisation des livreurs")
        
        for driver in drivers:
            driver_key = f"driver:{driver['id']}"
            
            # Stocker toutes les infos dans un hash
            self.r.hset(driver_key, mapping={
                'id': driver['id'],
                'name': driver['name'],
                'region': driver['region'],
                'rating': driver['rating'],
            })
            
            # Ajouter au sorted set par rating (pour requêtes rapides)
            self.r.zadd('drivers:ratings', {driver['id']: driver['rating']})
            
            # Ajouter à la liste de tous les livreurs
            self.r.sadd('drivers:all', driver['id'])
            
            # Initialiser les statistiques du livreur
            stats_key = f"driver:{driver['id']}:stats"
            self.r.hset(stats_key, mapping={
                'deliveries_in_progress': 0,
                'deliveries_completed': 0,
                'total_revenue': 0,
            })
        
        print_success(f"{len(drivers)} livreurs initialisés")
    
    def get_driver_rating(self, driver_id):
        """Accéder rapidement au rating d'un livreur"""
        return float(self.r.zscore('drivers:ratings', driver_id) or 0)
    
    def list_all_drivers(self):
        """Afficher la liste de tous les livreurs avec leur rating"""
        driver_ids = self.r.smembers('drivers:all')
        drivers_data = []
        
        for driver_id in driver_ids:
            driver_info = self.r.hgetall(f"driver:{driver_id}")
            drivers_data.append([
                driver_id,
                driver_info.get('name', 'N/A'),
                driver_info.get('region', 'N/A'),
                driver_info.get('rating', 'N/A')
            ])
        
        return sorted(drivers_data, key=lambda x: float(x[3]), reverse=True)
    
    def get_top_drivers(self, min_rating=4.7):
        """Chercher les meilleurs livreurs (rating >= min_rating)"""
        # zrangebyscore retourne les membres avec score >= min_rating
        top_drivers = self.r.zrangebyscore('drivers:ratings', min_rating, '+inf', withscores=True)
        return [(driver_id, rating) for driver_id, rating in top_drivers]
    
    # =====================================================================
    # TRAVAIL 2 : Gérer les commandes en cours
    # =====================================================================
    
    def initialize_orders(self, orders):
        """
        Initialiser les commandes dans Redis:
        - order:{id} : Hash contenant toutes les infos de la commande
        - orders:status:{status} : Set des IDs par statut
        """
        print_subheader("TRAVAIL 2 : Initialisation des commandes")
        
        for order in orders:
            order_key = f"order:{order['id']}"
            
            # Stocker toutes les infos dans un hash
            self.r.hset(order_key, mapping={
                'id': order['id'],
                'client': order['client'],
                'destination': order['destination'],
                'amount': order['amount'],
                'created_at': order['created_at'],
                'status': order['status'],
            })
            
            # Ajouter au set du statut correspondant
            status_key = f"orders:status:{order['status']}"
            self.r.sadd(status_key, order['id'])
        
        print_success(f"{len(orders)} commandes initialisées")
    
    def get_orders_by_status(self, status):
        """Récupérer toutes les commandes d'un statut donné"""
        return self.r.smembers(f"orders:status:{status}")
    
    # =====================================================================
    # TRAVAIL 3 : Affecter une commande à un livreur (ATOMIQUE)
    # =====================================================================
    
    def assign_order_atomic(self, order_id, driver_id):
        """
        Affecter atomiquement une commande à un livreur avec un script Lua
        Cette opération garantit l'atomicité de :
        1. Mise à jour du statut de la commande
        2. Enregistrement de l'affectation
        3. Incrémentation des livraisons en cours du livreur
        """
        print_subheader(f"TRAVAIL 3 : Affectation atomique de {order_id} à {driver_id}")
        
        # Script Lua pour garantir l'atomicité
        lua_script = """
        local order_id = KEYS[1]
        local driver_id = KEYS[2]
        local order_key = 'order:' .. order_id
        local driver_stats_key = 'driver:' .. driver_id .. ':stats'
        
        -- Vérifier que la commande existe et est en attente
        local current_status = redis.call('HGET', order_key, 'status')
        if not current_status then
            return {err = 'Commande inexistante'}
        end
        if current_status ~= 'en_attente' then
            return {err = 'Commande déjà assignée ou livrée'}
        end
        
        -- 1. Mettre à jour le statut de la commande
        redis.call('HSET', order_key, 'status', 'assignée')
        redis.call('HSET', order_key, 'driver_id', driver_id)
        
        -- 2. Déplacer la commande entre les sets de statut
        redis.call('SMOVE', 'orders:status:en_attente', 'orders:status:assignée', order_id)
        
        -- 3. Enregistrer l'affectation
        redis.call('SET', 'assignment:' .. order_id, driver_id)
        
        -- 4. Incrémenter les livraisons en cours du livreur
        redis.call('HINCRBY', driver_stats_key, 'deliveries_in_progress', 1)
        
        return 'OK'
        """
        
        try:
            result = self.r.eval(lua_script, 2, order_id, driver_id)
            print_success(f"Commande {order_id} assignée à {driver_id} de manière atomique")
            return True
        except Exception as e:
            print_error(f"Erreur lors de l'affectation: {e}")
            return False
    
    # =====================================================================
    # TRAVAIL 4 : Commandes affectées vs en attente
    # =====================================================================
    
    def display_orders_status(self):
        """Afficher toutes les commandes par statut"""
        print_subheader("TRAVAIL 4 : Commandes par statut")
        
        # Commandes en attente
        pending = self.get_orders_by_status('en_attente')
        print_info(f"Commandes en attente: {len(pending)}")
        if pending:
            print(f"  IDs: {', '.join(sorted(pending))}")
        
        # Commandes assignées
        assigned = self.get_orders_by_status('assignée')
        print_info(f"Commandes assignées: {len(assigned)}")
        if assigned:
            print(f"  IDs: {', '.join(sorted(assigned))}")
            # Afficher les affectations
            for order_id in sorted(assigned):
                driver_id = self.r.get(f"assignment:{order_id}")
                driver_name = self.r.hget(f"driver:{driver_id}", 'name')
                print(f"    {order_id} → {driver_id} ({driver_name})")
        
        # Commandes livrées
        delivered = self.get_orders_by_status('livrée')
        print_info(f"Commandes livrées: {len(delivered)}")
        if delivered:
            print(f"  IDs: {', '.join(sorted(delivered))}")
        
        # Livreur avec le rating maximal
        top_driver = self.r.zrevrange('drivers:ratings', 0, 0, withscores=True)
        if top_driver:
            driver_id, rating = top_driver[0]
            driver_name = self.r.hget(f"driver:{driver_id}", 'name')
            print_success(f"Meilleur livreur: {driver_id} ({driver_name}) - Rating: {rating}")
    
    # =====================================================================
    # TRAVAIL 5 : Simulation d'une livraison
    # =====================================================================
    
    def complete_delivery(self, order_id):
        """
        Simuler la fin d'une livraison:
        - Passer le statut à "livrée"
        - Décrémenter les livraisons en cours
        - Incrémenter les livraisons complétées
        """
        print_subheader(f"TRAVAIL 5 : Complétion de la livraison {order_id}")
        
        # Récupérer le livreur affecté
        driver_id = self.r.get(f"assignment:{order_id}")
        if not driver_id:
            print_error(f"Aucun livreur affecté à la commande {order_id}")
            return False
        
        # Récupérer le montant de la commande
        amount = float(self.r.hget(f"order:{order_id}", 'amount') or 0)
        
        # Script Lua pour atomicité
        lua_script = """
        local order_id = KEYS[1]
        local driver_id = KEYS[2]
        local amount = tonumber(ARGV[1])
        local order_key = 'order:' .. order_id
        local driver_stats_key = 'driver:' .. driver_id .. ':stats'
        
        -- 1. Mettre à jour le statut
        redis.call('HSET', order_key, 'status', 'livrée')
        
        -- 2. Déplacer entre les sets
        redis.call('SMOVE', 'orders:status:assignée', 'orders:status:livrée', order_id)
        
        -- 3. Décrémenter les livraisons en cours
        redis.call('HINCRBY', driver_stats_key, 'deliveries_in_progress', -1)
        
        -- 4. Incrémenter les livraisons complétées
        redis.call('HINCRBY', driver_stats_key, 'deliveries_completed', 1)
        
        -- 5. Ajouter au revenu total
        redis.call('HINCRBYFLOAT', driver_stats_key, 'total_revenue', amount)
        
        return 'OK'
        """
        
        try:
            self.r.eval(lua_script, 2, order_id, driver_id, amount)
            driver_name = self.r.hget(f"driver:{driver_id}", 'name')
            print_success(f"Livraison {order_id} complétée par {driver_id} ({driver_name})")
            print_info(f"Montant ajouté au revenu: {amount}€")
            return True
        except Exception as e:
            print_error(f"Erreur lors de la complétion: {e}")
            return False
    
    # =====================================================================
    # TRAVAIL 6 : État global du système (Dashboard)
    # =====================================================================
    
    def display_dashboard(self):
        """Afficher un dashboard temps réel du système"""
        print_header("DASHBOARD TEMPS RÉEL")
        
        # Nombre total de commandes par statut
        print_subheader("Commandes par statut")
        statuses = ['en_attente', 'assignée', 'livrée']
        status_data = []
        for status in statuses:
            count = self.r.scard(f"orders:status:{status}")
            status_data.append([status.upper(), count])
        print_table(['Statut', 'Nombre'], status_data)
        
        # Livraisons en cours par livreur
        print_subheader("Livraisons en cours par livreur")
        driver_ids = self.r.smembers('drivers:all')
        active_drivers = []
        for driver_id in driver_ids:
            in_progress = int(self.r.hget(f"driver:{driver_id}:stats", 'deliveries_in_progress') or 0)
            if in_progress > 0:
                driver_name = self.r.hget(f"driver:{driver_id}", 'name')
                active_drivers.append([driver_id, driver_name, in_progress])
        
        if active_drivers:
            print_table(['ID', 'Nom', 'En cours'], sorted(active_drivers, key=lambda x: x[2], reverse=True))
        else:
            print_info("Aucune livraison en cours")
        
        # Top 2 meilleurs livreurs
        print_subheader("Top 2 meilleurs livreurs")
        top_2 = self.r.zrevrange('drivers:ratings', 0, 1, withscores=True)
        top_data = []
        for driver_id, rating in top_2:
            driver_name = self.r.hget(f"driver:{driver_id}", 'name')
            region = self.r.hget(f"driver:{driver_id}", 'region')
            completed = self.r.hget(f"driver:{driver_id}:stats", 'deliveries_completed')
            revenue = self.r.hget(f"driver:{driver_id}:stats", 'total_revenue')
            top_data.append([driver_id, driver_name, region, rating, completed or 0, f"{float(revenue or 0)}€"])
        
        print_table(['ID', 'Nom', 'Région', 'Rating', 'Livrées', 'Revenu'], top_data)


def run_partie1():
    """Exécuter tous les travaux de la Partie 1"""
    
    print_header("PARTIE 1 : ÉTAT TEMPS RÉEL AVEC REDIS")
    
    # Connexion Redis
    r = get_redis_connection()
    if not r:
        print_error("Impossible de se connecter à Redis. Assurez-vous que Docker est lancé.")
        return
    
    # Nettoyer les données précédentes
    clear_redis(r)
    
    # Initialiser le système
    system = RedisDeliverySystem(r)
    
    # Générer des données (livreurs initiaux + données supplémentaires)
    initial_drivers = DataGenerator.get_initial_drivers()
    additional_drivers = DataGenerator.generate_drivers(20)
    all_drivers = initial_drivers + additional_drivers
    
    initial_orders = DataGenerator.get_initial_orders()
    additional_orders = DataGenerator.generate_orders(30)
    all_orders = initial_orders + additional_orders
    
    # TRAVAIL 1 : Initialiser les livreurs
    system.initialize_drivers(all_drivers)
    
    # Afficher quelques exemples
    print("\n--- Exemples de requêtes ---")
    print(f"Rating de d3: {system.get_driver_rating('d3')}")
    
    print("\nTop livreurs (rating >= 4.7):")
    top_drivers = system.get_top_drivers(4.7)
    for driver_id, rating in top_drivers[:5]:
        name = r.hget(f"driver:{driver_id}", 'name')
        print(f"  {driver_id} ({name}): {rating}")
    
    wait_for_input()
    
    # TRAVAIL 2 : Initialiser les commandes
    system.initialize_orders(all_orders)
    wait_for_input()
    
    # TRAVAIL 3 : Affecter c1 à d3
    system.assign_order_atomic('c1', 'd3')
    
    # Affecter quelques autres commandes
    system.assign_order_atomic('c2', 'd1')
    system.assign_order_atomic('c3', 'd2')
    wait_for_input()
    
    # TRAVAIL 4 : Afficher les statuts
    system.display_orders_status()
    wait_for_input()
    
    # TRAVAIL 5 : Compléter la livraison de c1
    system.complete_delivery('c1')
    wait_for_input()
    
    # TRAVAIL 6 : Dashboard
    system.display_dashboard()
    
    print_success("\n✓ Partie 1 terminée avec succès!")


if __name__ == "__main__":
    run_partie1()
