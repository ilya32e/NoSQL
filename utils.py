"""
Fonctions utilitaires pour le projet de gestion de livraisons
"""
import os
import redis
from pymongo import MongoClient
from dotenv import load_dotenv
from colorama import Fore, Style, init
from tabulate import tabulate

# Initialiser colorama pour Windows
init(autoreset=True)

# Charger les variables d'environnement
load_dotenv()


def get_redis_connection():
    """Créer une connexion à Redis"""
    try:
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        # Test de connexion
        r.ping()
        print(f"{Fore.GREEN}✓ Connexion Redis établie{Style.RESET_ALL}")
        return r
    except Exception as e:
        print(f"{Fore.RED}✗ Erreur connexion Redis: {e}{Style.RESET_ALL}")
        return None


def get_mongodb_connection():
    """Créer une connexion à MongoDB"""
    try:
        mongo_uri = f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/"
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Test de connexion
        client.admin.command('ping')
        db = client[os.getenv('MONGO_DATABASE', 'delivery')]
        print(f"{Fore.GREEN}✓ Connexion MongoDB établie{Style.RESET_ALL}")
        return db
    except Exception as e:
        print(f"{Fore.RED}✗ Erreur connexion MongoDB: {e}{Style.RESET_ALL}")
        return None


def print_header(title):
    """Afficher un en-tête formaté"""
    print(f"\n{Fore.CYAN}{'=' * 80}")
    print(f"{Fore.CYAN}{title.center(80)}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")


def print_subheader(title):
    """Afficher un sous-en-tête formaté"""
    print(f"\n{Fore.YELLOW}{'─' * 80}")
    print(f"{Fore.YELLOW}{title}")
    print(f"{Fore.YELLOW}{'─' * 80}{Style.RESET_ALL}\n")


def print_success(message):
    """Afficher un message de succès"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message):
    """Afficher un message d'erreur"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_info(message):
    """Afficher un message d'information"""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def print_warning(message):
    """Afficher un message d'avertissement"""
    print(f"{Fore.MAGENTA}⚠ {message}{Style.RESET_ALL}")


def print_table(headers, data, title=None):
    """Afficher des données sous forme de tableau"""
    if title:
        print(f"\n{Fore.CYAN}{title}{Style.RESET_ALL}")
    print(tabulate(data, headers=headers, tablefmt='grid'))
    print()


def clear_redis(r):
    """Nettoyer toutes les données Redis"""
    try:
        r.flushdb()
        print_success("Base Redis nettoyée")
    except Exception as e:
        print_error(f"Erreur lors du nettoyage Redis: {e}")


def clear_mongodb(db):
    """Nettoyer toutes les collections MongoDB"""
    try:
        collections = db.list_collection_names()
        for collection in collections:
            db[collection].drop()
        print_success("Base MongoDB nettoyée")
    except Exception as e:
        print_error(f"Erreur lors du nettoyage MongoDB: {e}")


def format_time(minutes):
    """Formater un temps en minutes en heures:minutes"""
    if minutes < 60:
        return f"{minutes}min"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h{mins:02d}min"


def format_currency(amount):
    """Formater un montant en euros"""
    return f"{amount}€"


def wait_for_input(message="Appuyez sur Entrée pour continuer..."):
    """Attendre une entrée utilisateur"""
    input(f"\n{Fore.YELLOW}{message}{Style.RESET_ALL}")
