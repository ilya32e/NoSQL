"""
PARTIE 3 : Structures avancées et cas limites

Ce script implémente:
- Travail 1: Gestion des livreurs multi-régions
- Travail 2: Cache avec expiration (TTL)
"""

import time
from utils import *
from data_generator import DataGenerator


class AdvancedRedisFeatures:
    """Fonctionnalités avancées Redis"""
    
    def __init__(self, redis_conn):
        self.r = redis_conn
    
    # =====================================================================
    # TRAVAIL 1 : Gestion des livreurs multi-régions
    # =====================================================================
    
    def setup_multi_region_drivers(self):
        """
        Modifier la structure Redis pour supporter les livreurs multi-régions
        Utilisation de Sets pour stocker les livreurs par région
        """
        print_subheader("TRAVAIL 1 : Gestion des livreurs multi-régions")
        
        # Configuration: certains livreurs opèrent dans plusieurs régions
        multi_region_drivers = {
            'd1': ['Paris', 'Banlieue'],  # Alice peut opérer partout
            'd2': ['Paris'],
            'd3': ['Banlieue'],
            'd4': ['Banlieue', 'Paris'],  # Diana aussi multi-régions
        }
        
        print_info("Configuration des régions par livreur:")
        
        for driver_id, regions in multi_region_drivers.items():
            # Stocker les régions du livreur dans un Set
            regions_key = f"driver:{driver_id}:regions"
            self.r.delete(regions_key)  # Nettoyer d'abord
            
            for region in regions:
                # Ajouter la région au set du livreur
                self.r.sadd(regions_key, region)
                
                # Ajouter le livreur au set de la région
                self.r.sadd(f"region:{region}:drivers", driver_id)
            
            driver_name = self.r.hget(f"driver:{driver_id}", 'name')
            print(f"  {driver_id} ({driver_name}): {', '.join(regions)}")
        
        print_success("Structure multi-régions configurée")
        
        print("\n--- Structure Redis ---")
        print_info("• driver:{id}:regions - Set des régions où opère le livreur")
        print_info("• region:{region}:drivers - Set des livreurs opérant dans la région")
    
    def find_drivers_in_region(self, region):
        """
        Trouver tous les livreurs opérant dans une région donnée
        """
        print_subheader(f"Recherche des livreurs dans la région: {region}")
        
        # Requête Redis: récupérer tous les membres du set
        driver_ids = self.r.smembers(f"region:{region}:drivers")
        
        if not driver_ids:
            print_warning(f"Aucun livreur trouvé dans {region}")
            return []
        
        # Récupérer les détails de chaque livreur
        drivers_data = []
        for driver_id in driver_ids:
            driver_info = self.r.hgetall(f"driver:{driver_id}")
            rating = self.r.zscore('drivers:ratings', driver_id)
            regions = self.r.smembers(f"driver:{driver_id}:regions")
            
            drivers_data.append([
                driver_id,
                driver_info.get('name', 'N/A'),
                ', '.join(sorted(regions)),
                rating or 'N/A'
            ])
        
        print_table(
            ['ID', 'Nom', 'Régions', 'Rating'],
            sorted(drivers_data),
            f"Livreurs opérant à {region}"
        )
        
        return driver_ids
    
    # =====================================================================
    # TRAVAIL 2 : Cache avec expiration (TTL)
    # =====================================================================
    
    def setup_cache_top_drivers(self, ttl=30):
        """
        Créer un cache des top 5 livreurs par rating
        avec expiration automatique (TTL) de 30 secondes
        """
        print_subheader("TRAVAIL 2 : Cache des top livreurs avec TTL")
        
        cache_key = 'cache:top_drivers'
        
        # Récupérer les top 5 livreurs
        top_drivers = self.r.zrevrange('drivers:ratings', 0, 4, withscores=True)
        
        # Stocker dans un cache avec TTL
        cache_data = []
        for driver_id, rating in top_drivers:
            driver_name = self.r.hget(f"driver:{driver_id}", 'name')
            cache_data.append(f"{driver_id}|{driver_name}|{rating}")
        
        # Stocker dans une liste Redis avec expiration
        self.r.delete(cache_key)
        if cache_data:
            self.r.rpush(cache_key, *cache_data)
            self.r.expire(cache_key, ttl)
        
        print_success(f"Cache créé avec {len(cache_data)} livreurs (TTL: {ttl}s)")
        print_info(f"Clé Redis: {cache_key}")
        
        # Afficher le cache
        self._display_cache(cache_key)
        
        return cache_key
    
    def setup_cache_pending_orders_by_region(self, ttl=30):
        """
        Créer un cache des commandes en attente par région
        avec expiration automatique
        """
        print_subheader("TRAVAIL 2 : Cache des commandes en attente par région avec TTL")
        
        # Récupérer toutes les commandes en attente
        pending_orders = self.r.smembers('orders:status:en_attente')
        
        # Grouper par région (basé sur la destination)
        regions_cache = {}
        
        for order_id in pending_orders:
            order_info = self.r.hgetall(f"order:{order_id}")
            destination = order_info.get('destination', 'Unknown')
            
            # Déterminer la région approximativement
            # (simplifié - en production, utiliser une vraie mapping)
            paris_locations = DataGenerator.get_paris_locations()
            if destination in paris_locations:
                region = 'Paris'
            else:
                region = 'Banlieue'
            
            if region not in regions_cache:
                regions_cache[region] = []
            
            regions_cache[region].append(order_id)
        
        # Stocker chaque région dans son propre cache
        cache_keys = []
        for region, order_ids in regions_cache.items():
            cache_key = f"cache:pending_orders:{region}"
            
            self.r.delete(cache_key)
            if order_ids:
                self.r.rpush(cache_key, *order_ids)
                self.r.expire(cache_key, ttl)
            
            cache_keys.append(cache_key)
            print_success(f"Cache '{region}': {len(order_ids)} commandes (TTL: {ttl}s)")
        
        return cache_keys
    
    def _display_cache(self, cache_key):
        """Afficher le contenu d'un cache"""
        ttl = self.r.ttl(cache_key)
        
        if ttl == -2:
            print_warning(f"Cache '{cache_key}' expiré ou inexistant")
            return
        
        cache_data = self.r.lrange(cache_key, 0, -1)
        
        if not cache_data:
            print_warning(f"Cache '{cache_key}' vide")
            return
        
        print(f"\n{Fore.CYAN}Contenu du cache '{cache_key}' (TTL: {ttl}s):{Style.RESET_ALL}")
        for item in cache_data:
            print(f"  • {item}")
    
    def demonstrate_cache_expiration(self):
        """
        Démonstration du fonctionnement des caches avec expiration
        """
        print_subheader("Démonstration de l'expiration des caches")
        
        print_info("Création de caches avec TTL de 10 secondes...")
        
        # Créer des caches
        cache_drivers = self.setup_cache_top_drivers(ttl=10)
        cache_orders = self.setup_cache_pending_orders_by_region(ttl=10)
        
        print_info("\nAttente de 5 secondes...")
        time.sleep(5)
        
        # Vérifier après 5 secondes
        print_info("Vérification après 5 secondes:")
        self._display_cache(cache_drivers)
        
        print_info("\nAttente de 6 secondes supplémentaires (total: 11s)...")
        time.sleep(6)
        
        # Vérifier après expiration
        print_info("Vérification après expiration:")
        self._display_cache(cache_drivers)
        
        print_success("\nLe cache a bien expiré automatiquement!")
    
    def refresh_cache_function(self):
        """
        Fonction Python pour réactualiser les caches
        À appeler périodiquement ou sur événement
        """
        print_subheader("Fonction de rafraîchissement des caches")
        
        print_info("Cette fonction peut être appelée:")
        print("  • Périodiquement (toutes les 30 secondes)")
        print("  • Sur événement (nouvelle commande, changement de rating)")
        print("  • Manuellement pour forcer le rafraîchissement")
        
        # Rafraîchir les caches
        self.setup_cache_top_drivers(ttl=30)
        self.setup_cache_pending_orders_by_region(ttl=30)
        
        print_success("Caches rafraîchis avec succès")
        
        # Exemple de pseudocode pour un rafraîchissement automatique
        pseudocode = """
# Pseudocode pour rafraîchissement automatique
def auto_refresh_caches():
    while True:
        try:
            # Rafraîchir les caches
            refresh_cache_function()
            
            # Attendre 30 secondes
            time.sleep(30)
        except Exception as e:
            log_error(e)
            time.sleep(5)  # Retry après erreur

# Lancer en arrière-plan
threading.Thread(target=auto_refresh_caches, daemon=True).start()
        """
        
        print(f"\n{Fore.YELLOW}Exemple d'implémentation:{Style.RESET_ALL}")
        print(pseudocode)


def run_partie3():
    """Exécuter tous les travaux de la Partie 3"""
    
    print_header("PARTIE 3 : STRUCTURES AVANCÉES ET CAS LIMITES")
    
    # Connexion Redis
    r = get_redis_connection()
    if not r:
        print_error("Impossible de se connecter à Redis")
        return
    
    # Initialiser le système
    advanced = AdvancedRedisFeatures(r)
    
    # TRAVAIL 1 : Multi-régions
    advanced.setup_multi_region_drivers()
    wait_for_input()
    
    # Rechercher les livreurs dans différentes régions
    advanced.find_drivers_in_region('Paris')
    wait_for_input()
    
    advanced.find_drivers_in_region('Banlieue')
    wait_for_input()
    
    # TRAVAIL 2 : Cache avec TTL
    advanced.setup_cache_top_drivers(ttl=30)
    wait_for_input()
    
    advanced.setup_cache_pending_orders_by_region(ttl=30)
    wait_for_input()
    
    # Fonction de rafraîchissement
    advanced.refresh_cache_function()
    wait_for_input()
    
    # Démonstration d'expiration (optionnel)
    print_info("\nVoulez-vous voir une démonstration de l'expiration des caches?")
    print_info("(Cela prendra 12 secondes)")
    response = input("Continuer? (o/n): ")
    if response.lower() == 'o':
        advanced.demonstrate_cache_expiration()
    
    print_success("\n✓ Partie 3 terminée avec succès!")


if __name__ == "__main__":
    run_partie3()
