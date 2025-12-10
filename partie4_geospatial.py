"""
PARTIE 4 : Geo-spatial (Localisation en temps réel)

Ce script implémente:
- Travail 1: Stocker les positions géo-spatiales
- Travail 2: Trouver les livreurs proches
- Travail 3: Cas d'usage - Affectation optimale
- Travail 4: Monitoring des livreurs (Bonus)
"""

import random
import math
from utils import *
from data_generator import DataGenerator


class GeoSpatialDelivery:
    """Gestion géo-spatiale avec Redis"""
    
    # Coordonnées du centre de Paris (approximatif)
    PARIS_CENTER = {'lon': 2.3522, 'lat': 48.8566}
    
    def __init__(self, redis_conn):
        self.r = redis_conn
    
    # =====================================================================
    # TRAVAIL 1 : Stocker les positions géo-spatiales
    # =====================================================================
    
    def store_delivery_points(self):
        """
        Créer un index géo-spatial Redis pour les lieux de livraison
        Utilisation de GEOADD
        """
        print_subheader("TRAVAIL 1 : Stockage des positions géo-spatiales")
        
        geo_index = 'delivery_points'
        
        # Récupérer les lieux de Paris et banlieue
        paris_locations = DataGenerator.get_paris_locations()
        banlieue_locations = DataGenerator.get_banlieue_locations()
        all_locations = {**paris_locations, **banlieue_locations}
        
        print_info(f"Ajout de {len(all_locations)} lieux de livraison...")
        
        # GEOADD: longitude, latitude, nom
        # Using execute_command to avoid redis-py 5.0.1 bug with nx/xx parameters
        for location_name, coords in all_locations.items():
            self.r.execute_command('GEOADD', geo_index, coords['lon'], coords['lat'], location_name)
        
        print_success(f"Index géo-spatial '{geo_index}' créé avec {len(all_locations)} lieux")
        
        # Afficher quelques exemples
        sample_data = []
        for loc, coords in list(all_locations.items())[:5]:
            sample_data.append([loc, coords['lon'], coords['lat']])
        
        print_table(['Lieu', 'Longitude', 'Latitude'], sample_data, "Exemples de lieux")
    
    def store_driver_locations(self):
        """
        Créer un index géo-spatial pour les positions actuelles des livreurs
        """
        print_subheader("Stockage des positions des livreurs")
        
        geo_index = 'drivers_locations'
        
        # Positions initiales des livreurs (selon le sujet)
        driver_positions = {
            'd1': {'lon': 2.365, 'lat': 48.862},  # Paris
            'd2': {'lon': 2.378, 'lat': 48.871},  # Paris
            'd3': {'lon': 2.320, 'lat': 48.920},  # Banlieue
            'd4': {'lon': 2.400, 'lat': 48.750},  # Banlieue
        }
        
        print_info(f"Ajout de {len(driver_positions)} livreurs...")
        
        # Using execute_command to avoid redis-py 5.0.1 bug
        for driver_id, coords in driver_positions.items():
            self.r.execute_command('GEOADD', geo_index, coords['lon'], coords['lat'], driver_id)
        
        print_success(f"Index géo-spatial '{geo_index}' créé avec {len(driver_positions)} livreurs")
        
        # Afficher les positions
        position_data = []
        for driver_id, coords in driver_positions.items():
            driver_name = self.r.hget(f"driver:{driver_id}", 'name')
            position_data.append([driver_id, driver_name or 'N/A', coords['lon'], coords['lat']])
        
        print_table(['ID', 'Nom', 'Longitude', 'Latitude'], position_data, "Positions actuelles")
    
    # =====================================================================
    # TRAVAIL 2 : Trouver les livreurs proches
    # =====================================================================
    
    def find_drivers_within_radius(self, location, radius_km):
        """
        Trouver tous les livreurs dans un rayon donné autour d'un lieu
        """
        print_subheader(f"Livreurs dans un rayon de {radius_km}km autour de {location}")
        
        # Récupérer les coordonnées du lieu
        location_coords = self.r.geopos('delivery_points', location)
        
        if not location_coords or not location_coords[0]:
            print_error(f"Lieu '{location}' non trouvé")
            return []
        
        lon, lat = location_coords[0]
        
        # GEORADIUS: chercher dans un rayon (en km)
        drivers = self.r.georadius(
            'drivers_locations',
            lon,
            lat,
            radius_km,
            unit='km',
            withdist=True,
            withcoord=True,
            sort='ASC'
        )
        
        if not drivers:
            print_warning(f"Aucun livreur trouvé dans un rayon de {radius_km}km")
            return []
        
        # Afficher les résultats
        driver_data = []
        for driver_id, distance, coords in drivers:
            driver_name = self.r.hget(f"driver:{driver_id}", 'name')
            rating = self.r.zscore('drivers:ratings', driver_id)
            driver_data.append([
                driver_id,
                driver_name or 'N/A',
                f"{distance:.2f} km",
                f"{coords[0]:.4f}, {coords[1]:.4f}",
                rating or 'N/A'
            ])
        
        print_table(
            ['ID', 'Nom', 'Distance', 'Coordonnées', 'Rating'],
            driver_data,
            f"Livreurs à moins de {radius_km}km de {location}"
        )
        
        return drivers
    
    def get_closest_drivers(self, location, count=2):
        """
        Récupérer les N livreurs les plus proches d'un lieu
        """
        print_subheader(f"Les {count} livreurs les plus proches de {location}")
        
        # Récupérer les coordonnées du lieu
        location_coords = self.r.geopos('delivery_points', location)
        
        if not location_coords or not location_coords[0]:
            print_error(f"Lieu '{location}' non trouvé")
            return []
        
        lon, lat = location_coords[0]
        
        # GEORADIUS avec count
        drivers = self.r.georadius(
            'drivers_locations',
            lon,
            lat,
            100,  # rayon large pour être sûr
            unit='km',
            withdist=True,
            count=count,
            sort='ASC'
        )
        
        if not drivers:
            print_warning("Aucun livreur trouvé")
            return []
        
        # Afficher les résultats
        driver_data = []
        for driver_id, distance in drivers:
            driver_name = self.r.hget(f"driver:{driver_id}", 'name')
            rating = self.r.zscore('drivers:ratings', driver_id)
            driver_data.append([
                driver_id,
                driver_name or 'N/A',
                f"{distance:.2f} km",
                rating or 'N/A'
            ])
        
        print_table(
            ['ID', 'Nom', 'Distance', 'Rating'],
            driver_data,
            f"Top {count} livreurs les plus proches"
        )
        
        return drivers
    
    # =====================================================================
    # TRAVAIL 3 : Cas d'usage - Affectation optimale
    # =====================================================================
    
    def optimal_assignment(self, location, radius_km=3, strategy='closest'):
        """
        Affecter une nouvelle commande au meilleur livreur
        
        Stratégies possibles:
        - 'closest': le plus proche
        - 'best_rated': le mieux noté
        - 'balanced': compromis distance/rating
        """
        print_subheader(f"Affectation optimale pour {location}")
        print_info(f"Stratégie: {strategy}")
        print_info(f"Rayon de recherche: {radius_km}km")
        
        # Récupérer les coordonnées du lieu
        location_coords = self.r.geopos('delivery_points', location)
        
        if not location_coords or not location_coords[0]:
            print_error(f"Lieu '{location}' non trouvé")
            return None
        
        lon, lat = location_coords[0]
        
        # Trouver les livreurs dans le rayon
        drivers = self.r.georadius(
            'drivers_locations',
            lon,
            lat,
            radius_km,
            unit='km',
            withdist=True,
            sort='ASC'
        )
        
        if not drivers:
            print_warning(f"Aucun livreur disponible dans un rayon de {radius_km}km")
            return None
        
        # Récupérer les détails de chaque livreur
        candidates = []
        for driver_id, distance in drivers:
            driver_name = self.r.hget(f"driver:{driver_id}", 'name')
            rating = float(self.r.zscore('drivers:ratings', driver_id) or 0)
            in_progress = int(self.r.hget(f"driver:{driver_id}:stats", 'deliveries_in_progress') or 0)
            
            # Calculer un score selon la stratégie
            if strategy == 'closest':
                score = -distance  # Plus proche = meilleur score
            elif strategy == 'best_rated':
                score = rating
            elif strategy == 'balanced':
                # Compromis: rating élevé et distance faible
                # Normaliser: rating [0-5] et distance [0-10km]
                score = rating * 2 - distance
            else:
                score = 0
            
            candidates.append({
                'driver_id': driver_id,
                'name': driver_name,
                'distance': distance,
                'rating': rating,
                'in_progress': in_progress,
                'score': score
            })
        
        # Trier par score décroissant
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Afficher tous les candidats
        candidate_data = []
        for c in candidates:
            candidate_data.append([
                c['driver_id'],
                c['name'],
                f"{c['distance']:.2f} km",
                c['rating'],
                c['in_progress'],
                f"{c['score']:.2f}"
            ])
        
        print_table(
            ['ID', 'Nom', 'Distance', 'Rating', 'En cours', 'Score'],
            candidate_data,
            "Candidats triés par score"
        )
        
        # Sélectionner le meilleur
        best = candidates[0]
        print_success(f"\n✓ Meilleur choix: {best['driver_id']} ({best['name']})")
        print_info(f"  Distance: {best['distance']:.2f}km")
        print_info(f"  Rating: {best['rating']}")
        print_info(f"  Livraisons en cours: {best['in_progress']}")
        
        return best
    
    # =====================================================================
    # TRAVAIL 4 : Monitoring des livreurs (Bonus)
    # =====================================================================
    
    def update_driver_position(self, driver_id, new_lon, new_lat):
        """
        Mettre à jour la position d'un livreur en temps réel
        """
        # GEOADD met à jour automatiquement si le membre existe
        # Using execute_command to avoid redis-py 5.0.1 bug
        self.r.execute_command('GEOADD', 'drivers_locations', new_lon, new_lat, driver_id)
        
        driver_name = self.r.hget(f"driver:{driver_id}", 'name')
        print_success(f"Position de {driver_id} ({driver_name}) mise à jour: ({new_lon:.4f}, {new_lat:.4f})")
    
    def check_driver_in_zone(self, driver_id, max_distance_km=5):
        """
        Détecter si un livreur sort de sa zone de service
        (> 5km du centre de Paris)
        """
        # Récupérer la position actuelle du livreur
        position = self.r.geopos('drivers_locations', driver_id)
        
        if not position or not position[0]:
            print_warning(f"Position de {driver_id} non trouvée")
            return False
        
        lon, lat = position[0]
        
        # Calculer la distance au centre de Paris
        distance = self._calculate_distance(
            self.PARIS_CENTER['lon'],
            self.PARIS_CENTER['lat'],
            lon,
            lat
        )
        
        driver_name = self.r.hget(f"driver:{driver_id}", 'name')
        
        if distance > max_distance_km:
            print_warning(f"⚠ ALERTE: {driver_id} ({driver_name}) est hors zone!")
            print_info(f"  Distance du centre: {distance:.2f}km (limite: {max_distance_km}km)")
            return False
        else:
            print_success(f"✓ {driver_id} ({driver_name}) est dans la zone ({distance:.2f}km)")
            return True
    
    def simulate_real_time_monitoring(self):
        """
        Simuler un monitoring temps réel des livreurs
        """
        print_subheader("TRAVAIL 4 : Monitoring temps réel")
        
        print_info("Simulation: déplacement de d1 toutes les 'secondes'")
        
        # Positions successives de d1 (simulées)
        movements = [
            {'lon': 2.365, 'lat': 48.862, 'desc': 'Position initiale'},
            {'lon': 2.370, 'lat': 48.865, 'desc': 'Déplacement vers le nord'},
            {'lon': 2.375, 'lat': 48.870, 'desc': 'Continue vers le nord'},
            {'lon': 2.380, 'lat': 48.875, 'desc': 'Encore plus au nord'},
            {'lon': 2.450, 'lat': 48.950, 'desc': 'HORS ZONE - trop loin!'},
        ]
        
        for i, move in enumerate(movements):
            print(f"\n--- Mise à jour {i+1} ---")
            print_info(move['desc'])
            
            # Mettre à jour la position
            self.update_driver_position('d1', move['lon'], move['lat'])
            
            # Vérifier si dans la zone
            self.check_driver_in_zone('d1', max_distance_km=5)
            
            if i < len(movements) - 1:
                wait_for_input("Continuer la simulation?")
        
        # Pseudocode pour implémentation réelle
        pseudocode = """
# Pseudocode pour monitoring temps réel
def monitor_drivers_loop():
    while True:
        # Récupérer tous les livreurs actifs
        active_drivers = get_active_drivers()
        
        for driver in active_drivers:
            # Recevoir la nouvelle position (GPS du téléphone)
            new_position = receive_gps_update(driver.id)
            
            # Mettre à jour dans Redis
            update_driver_position(driver.id, new_position.lon, new_position.lat)
            
            # Vérifier la zone
            if not check_driver_in_zone(driver.id):
                # Envoyer une alerte
                send_alert(driver.id, "Vous êtes hors de votre zone de service")
                notify_admin(driver.id, "Livreur hors zone")
        
        # Attendre 10 secondes avant la prochaine mise à jour
        time.sleep(10)

# Lancer le monitoring en arrière-plan
threading.Thread(target=monitor_drivers_loop, daemon=True).start()
        """
        
        print(f"\n{Fore.YELLOW}Exemple d'implémentation temps réel:{Style.RESET_ALL}")
        print(pseudocode)
    
    @staticmethod
    def _calculate_distance(lon1, lat1, lon2, lat2):
        """
        Calculer la distance entre deux points GPS (formule de Haversine)
        Retourne la distance en kilomètres
        """
        # Rayon de la Terre en km
        R = 6371
        
        # Conversion en radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Formule de Haversine
        a = (math.sin(delta_lat/2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon/2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        return distance


def run_partie4():
    """Exécuter tous les travaux de la Partie 4"""
    
    print_header("PARTIE 4 : GEO-SPATIAL (LOCALISATION TEMPS RÉEL)")
    
    # Connexion Redis
    r = get_redis_connection()
    if not r:
        print_error("Impossible de se connecter à Redis")
        return
    
    # Initialiser le système
    geo = GeoSpatialDelivery(r)
    
    # TRAVAIL 1 : Stocker les positions
    geo.store_delivery_points()
    wait_for_input()
    
    geo.store_driver_locations()
    wait_for_input()
    
    # TRAVAIL 2 : Trouver les livreurs proches
    geo.find_drivers_within_radius('Marais', 2)
    wait_for_input()
    
    geo.get_closest_drivers('Marais', 2)
    wait_for_input()
    
    # TRAVAIL 3 : Affectation optimale
    print_info("\nTest de différentes stratégies d'affectation:")
    
    print("\n=== Stratégie: Plus proche ===")
    geo.optimal_assignment('Marais', radius_km=3, strategy='closest')
    wait_for_input()
    
    print("\n=== Stratégie: Mieux noté ===")
    geo.optimal_assignment('Marais', radius_km=3, strategy='best_rated')
    wait_for_input()
    
    print("\n=== Stratégie: Équilibrée (distance + rating) ===")
    geo.optimal_assignment('Marais', radius_km=3, strategy='balanced')
    wait_for_input()
    
    # TRAVAIL 4 : Monitoring
    geo.simulate_real_time_monitoring()
    
    print_success("\n✓ Partie 4 terminée avec succès!")


if __name__ == "__main__":
    run_partie4()
