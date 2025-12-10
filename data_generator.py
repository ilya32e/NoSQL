"""
Générateur de données de test pour le système de livraisons
"""
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('fr_FR')


class DataGenerator:
    """Générateur de données réalistes pour le projet"""
    
    # Régions de Paris et banlieue
    REGIONS = ['Paris', 'Banlieue']
    
    # Quartiers de Paris avec coordonnées GPS approximatives
    PARIS_LOCATIONS = {
        'Marais': {'lon': 2.364, 'lat': 48.861},
        'Belleville': {'lon': 2.379, 'lat': 48.870},
        'Bercy': {'lon': 2.381, 'lat': 48.840},
        'Auteuil': {'lon': 2.254, 'lat': 48.851},
        'Montmartre': {'lon': 2.341, 'lat': 48.886},
        'Latin Quarter': {'lon': 2.344, 'lat': 48.851},
        'Bastille': {'lon': 2.369, 'lat': 48.853},
        'Opéra': {'lon': 2.331, 'lat': 48.871},
        'Champs-Élysées': {'lon': 2.307, 'lat': 48.869},
        'Nation': {'lon': 2.396, 'lat': 48.848},
    }
    
    # Banlieue avec coordonnées
    BANLIEUE_LOCATIONS = {
        'Montreuil': {'lon': 2.444, 'lat': 48.863},
        'Vincennes': {'lon': 2.439, 'lat': 48.847},
        'Saint-Denis': {'lon': 2.359, 'lat': 48.936},
        'Levallois': {'lon': 2.287, 'lat': 48.893},
        'Neuilly': {'lon': 2.269, 'lat': 48.884},
        'Boulogne': {'lon': 2.239, 'lat': 48.835},
    }
    
    # Statuts de commande
    ORDER_STATUSES = ['en_attente', 'assignée', 'livrée']
    
    @staticmethod
    def generate_drivers(count=50):
        """Générer des livreurs"""
        drivers = []
        for i in range(count):
            driver_id = f"d{i+1}"
            driver = {
                'id': driver_id,
                'name': fake.name(),
                'region': random.choice(DataGenerator.REGIONS),
                'rating': round(random.uniform(3.5, 5.0), 1),
                'phone': fake.phone_number(),
                'email': fake.email(),
            }
            drivers.append(driver)
        return drivers
    
    @staticmethod
    def generate_driver_positions(drivers):
        """Générer des positions GPS pour les livreurs"""
        positions = []
        for driver in drivers:
            if driver['region'] == 'Paris':
                base_coords = random.choice(list(DataGenerator.PARIS_LOCATIONS.values()))
            else:
                base_coords = random.choice(list(DataGenerator.BANLIEUE_LOCATIONS.values()))
            
            # Ajouter une légère variation
            position = {
                'driver_id': driver['id'],
                'lon': round(base_coords['lon'] + random.uniform(-0.01, 0.01), 6),
                'lat': round(base_coords['lat'] + random.uniform(-0.01, 0.01), 6),
            }
            positions.append(position)
        return positions
    
    @staticmethod
    def generate_orders(count=100):
        """Générer des commandes"""
        orders = []
        all_locations = list(DataGenerator.PARIS_LOCATIONS.keys()) + list(DataGenerator.BANLIEUE_LOCATIONS.keys())
        
        base_time = datetime.now() - timedelta(hours=3)
        
        for i in range(count):
            order_id = f"c{i+1}"
            created_at = base_time + timedelta(minutes=random.randint(0, 180))
            
            order = {
                'id': order_id,
                'client': f"Client {fake.last_name()}",
                'destination': random.choice(all_locations),
                'amount': random.randint(10, 80),
                'created_at': created_at.isoformat(),
                'status': random.choice(DataGenerator.ORDER_STATUSES),
            }
            orders.append(order)
        return orders
    
    @staticmethod
    def generate_deliveries(drivers, orders, count=200):
        """Générer un historique de livraisons pour MongoDB"""
        deliveries = []
        
        for i in range(min(count, len(orders))):
            driver = random.choice(drivers)
            order = orders[i % len(orders)]
            
            # Coordonnées de destination
            all_locations = {**DataGenerator.PARIS_LOCATIONS, **DataGenerator.BANLIEUE_LOCATIONS}
            destination = order['destination']
            dest_coords = all_locations.get(destination, list(all_locations.values())[0])
            
            # Région basée sur la destination
            if destination in DataGenerator.PARIS_LOCATIONS:
                region = 'Paris'
            else:
                region = 'Banlieue'
            
            # Temps de livraison
            pickup_time = datetime.fromisoformat(order['created_at'])
            duration_minutes = random.randint(10, 45)
            delivery_time = pickup_time + timedelta(minutes=duration_minutes)
            
            # Avis client
            reviews = [
                "Excellent service!",
                "Très professionnel",
                "Livraison rapide, merci!",
                "Parfait comme toujours",
                "Très sympathique",
                "Super livreur!",
                "Impeccable",
                "RAS, tout s'est bien passé",
                "Très ponctuel",
                "Je recommande",
            ]
            
            delivery = {
                'command_id': order['id'],
                'client': order['client'],
                'driver_id': driver['id'],
                'driver_name': driver['name'],
                'pickup_time': pickup_time,
                'delivery_time': delivery_time,
                'duration_minutes': duration_minutes,
                'amount': order['amount'],
                'region': region,
                'rating': driver['rating'],
                'review': random.choice(reviews),
                'status': 'completed',
                'destination': destination,
                'destination_coords': dest_coords,
            }
            deliveries.append(delivery)
        
        return deliveries
    
    @staticmethod
    def get_initial_drivers():
        """Retourner les livreurs initiaux du projet"""
        return [
            {'id': 'd1', 'name': 'Alice Dupont', 'region': 'Paris', 'rating': 4.8},
            {'id': 'd2', 'name': 'Bob Martin', 'region': 'Paris', 'rating': 4.5},
            {'id': 'd3', 'name': 'Charlie Lefevre', 'region': 'Banlieue', 'rating': 4.9},
            {'id': 'd4', 'name': 'Diana Russo', 'region': 'Banlieue', 'rating': 4.3},
        ]
    
    @staticmethod
    def get_initial_orders():
        """Retourner les commandes initiales du projet"""
        return [
            {'id': 'c1', 'client': 'Client A', 'destination': 'Marais', 'amount': 25, 'created_at': '2025-12-06T14:00:00', 'status': 'en_attente'},
            {'id': 'c2', 'client': 'Client B', 'destination': 'Belleville', 'amount': 15, 'created_at': '2025-12-06T14:05:00', 'status': 'en_attente'},
            {'id': 'c3', 'client': 'Client C', 'destination': 'Bercy', 'amount': 30, 'created_at': '2025-12-06T14:10:00', 'status': 'en_attente'},
            {'id': 'c4', 'client': 'Client D', 'destination': 'Auteuil', 'amount': 20, 'created_at': '2025-12-06T14:15:00', 'status': 'en_attente'},
        ]
    
    @staticmethod
    def get_paris_locations():
        """Retourner les lieux de Paris"""
        return DataGenerator.PARIS_LOCATIONS
    
    @staticmethod
    def get_banlieue_locations():
        """Retourner les lieux de banlieue"""
        return DataGenerator.BANLIEUE_LOCATIONS


if __name__ == "__main__":
    # Test du générateur
    print("=== Test du générateur de données ===\n")
    
    drivers = DataGenerator.generate_drivers(10)
    print(f"Généré {len(drivers)} livreurs")
    print(f"Exemple: {drivers[0]}\n")
    
    orders = DataGenerator.generate_orders(20)
    print(f"Généré {len(orders)} commandes")
    print(f"Exemple: {orders[0]}\n")
    
    positions = DataGenerator.generate_driver_positions(drivers)
    print(f"Généré {len(positions)} positions")
    print(f"Exemple: {positions[0]}\n")
    
    deliveries = DataGenerator.generate_deliveries(drivers, orders, 30)
    print(f"Généré {len(deliveries)} livraisons")
    print(f"Exemple: {deliveries[0]}\n")
