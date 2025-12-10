"""
Script de test et vérification complète du projet NoSQL
Ce script vérifie que tout fonctionne correctement
"""

import sys
from colorama import Fore, Style, init

init(autoreset=True)

def print_header(title):
    print(f"\n{Fore.CYAN}{'=' * 80}")
    print(f"{Fore.CYAN}{title.center(80)}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")

def print_success(msg):
    print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")

def print_error(msg):
    print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")

def print_info(msg):
    print(f"{Fore.YELLOW}ℹ {msg}{Style.RESET_ALL}")

def test_imports():
    """Tester que toutes les bibliothèques sont installées"""
    print_header("TEST 1: Vérification des imports Python")
    
    libraries = [
        ('redis', 'Redis client'),
        ('pymongo', 'MongoDB client'),
        ('faker', 'Générateur de données'),
        ('colorama', 'Coloration terminal'),
        ('tabulate', 'Affichage tableaux'),
        ('dotenv', 'Variables d\'environnement')
    ]
    
    all_ok = True
    for lib, desc in libraries:
        try:
            __import__(lib)
            print_success(f"{desc} ({lib})")
        except ImportError:
            print_error(f"{desc} ({lib}) - MANQUANT")
            all_ok = False
    
    return all_ok

def test_files():
    """Vérifier que tous les fichiers nécessaires existent"""
    print_header("TEST 2: Vérification des fichiers du projet")
    
    import os
    
    required_files = [
        ('docker-compose.yml', 'Configuration Docker'),
        ('requirements.txt', 'Dépendances Python'),
        ('.env', 'Variables d\'environnement'),
        ('utils.py', 'Fonctions utilitaires'),
        ('data_generator.py', 'Générateur de données'),
        ('partie1_redis_temps_reel.py', 'Partie 1: Redis'),
        ('partie2_mongodb_historique.py', 'Partie 2: MongoDB'),
        ('partie3_avancees.py', 'Partie 3: Avancé'),
        ('partie4_geospatial.py', 'Partie 4: Geo-spatial'),
        ('main_demo.py', 'Script principal'),
        ('README.md', 'Guide rapide'),
        ('DOCUMENTATION.md', 'Documentation complète'),
    ]
    
    all_ok = True
    for filename, desc in required_files:
        if os.path.exists(filename):
            print_success(f"{desc}: {filename}")
        else:
            print_error(f"{desc}: {filename} - MANQUANT")
            all_ok = False
    
    return all_ok

def test_redis_connection():
    """Tester la connexion Redis"""
    print_header("TEST 3: Connexion Redis")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        print_success("Connexion Redis établie")
        
        # Test basique
        r.set('test_key', 'test_value')
        val = r.get('test_key')
        if val == 'test_value':
            print_success("Lecture/Écriture Redis fonctionne")
        r.delete('test_key')
        
        return True
    except Exception as e:
        print_error(f"Connexion Redis échouée: {e}")
        print_info("  → Assurez-vous que Docker Desktop est lancé")
        print_info("  → Exécutez: docker-compose up -d")
        return False

def test_mongodb_connection():
    """Tester la connexion MongoDB"""
    print_header("TEST 4: Connexion MongoDB")
    
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://admin:admin123@localhost:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print_success("Connexion MongoDB établie")
        
        # Test basique
        db = client['test_db']
        collection = db['test_collection']
        collection.insert_one({'test': 'value'})
        result = collection.find_one({'test': 'value'})
        if result:
            print_success("Lecture/Écriture MongoDB fonctionne")
        collection.drop()
        
        return True
    except Exception as e:
        print_error(f"Connexion MongoDB échouée: {e}")
        print_info("  → Assurez-vous que Docker Desktop est lancé")
        print_info("  → Exécutez: docker-compose up -d")
        print_info("  → Attendez ~10 secondes que MongoDB démarre")
        return False

def test_code_syntax():
    """Vérifier que tous les scripts Python sont valides"""
    print_header("TEST 5: Syntaxe des scripts Python")
    
    import py_compile
    import os
    
    scripts = [
        'utils.py',
        'data_generator.py',
        'partie1_redis_temps_reel.py',
        'partie2_mongodb_historique.py',
        'partie3_avancees.py',
        'partie4_geospatial.py',
        'main_demo.py',
    ]
    
    all_ok = True
    for script in scripts:
        if os.path.exists(script):
            try:
                py_compile.compile(script, doraise=True)
                print_success(f"Syntaxe valide: {script}")
            except py_compile.PyCompileError as e:
                print_error(f"Erreur syntaxe: {script}")
                print(f"  {e}")
                all_ok = False
        else:
            print_error(f"Fichier manquant: {script}")
            all_ok = False
    
    return all_ok

def main():
    """Fonction principale de test"""
    print_header("VÉRIFICATION COMPLÈTE DU PROJET NOSQL")
    
    print_info("Ce script vérifie que tout est correctement installé et configuré.\n")
    
    results = {}
    
    # Test 1: Imports
    results['imports'] = test_imports()
    
    # Test 2: Fichiers
    results['files'] = test_files()
    
    # Test 3: Syntaxe
    results['syntax'] = test_code_syntax()
    
    # Test 4: Redis (seulement si imports OK)
    if results['imports']:
        results['redis'] = test_redis_connection()
    else:
        print_info("\n⚠ Skip test Redis (imports manquants)")
        results['redis'] = False
    
    # Test 5: MongoDB (seulement si imports OK)
    if results['imports']:
        results['mongodb'] = test_mongodb_connection()
    else:
        print_info("\n⚠ Skip test MongoDB (imports manquants)")
        results['mongodb'] = False
    
    # Résumé final
    print_header("RÉSUMÉ DES TESTS")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        color = Fore.GREEN if result else Fore.RED
        print(f"{color}{status}{Style.RESET_ALL} - {test_name.upper()}")
    
    print(f"\n{Fore.CYAN}Score: {passed}/{total} tests réussis{Style.RESET_ALL}")
    
    if passed == total:
        print(f"\n{Fore.GREEN}{'🎉 TOUS LES TESTS SONT PASSÉS ! 🎉'.center(80)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'Le projet est prêt à être exécuté.'.center(80)}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Prochaine étape:{Style.RESET_ALL}")
        print(f"  python main_demo.py")
        return 0
    else:
        print(f"\n{Fore.RED}{'⚠ CERTAINS TESTS ONT ÉCHOUÉ ⚠'.center(80)}{Style.RESET_ALL}")
        
        if not results['imports']:
            print(f"\n{Fore.YELLOW}Pour corriger les imports:{Style.RESET_ALL}")
            print(f"  pip install -r requirements.txt")
        
        if not (results.get('redis', True) and results.get('mongodb', True)):
            print(f"\n{Fore.YELLOW}Pour corriger Redis/MongoDB:{Style.RESET_ALL}")
            print(f"  1. Lancer Docker Desktop")
            print(f"  2. docker-compose up -d")
            print(f"  3. Attendre 10-15 secondes")
            print(f"  4. Relancer ce script de test")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
