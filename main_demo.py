"""
Script principal - Démonstration complète du projet NoSQL

Ce script orchestre toutes les parties du projet et offre un menu interactif
pour exécuter chaque partie séparément ou toutes ensemble.
"""

import sys
from utils import *

# Importer les modules de chaque partie
try:
    from partie1_redis_temps_reel import run_partie1
    from partie2_mongodb_historique import run_partie2
    from partie3_avancees import run_partie3
    from partie4_geospatial import run_partie4
except ImportError as e:
    print_error(f"Erreur d'import: {e}")
    print_info("Assurez-vous que tous les fichiers sont présents")
    sys.exit(1)


def display_welcome():
    """Afficher l'écran de bienvenue"""
    print_header("PROJET NOSQL - SYSTÈME DE GESTION DE LIVRAISONS")
    print(f"{Fore.CYAN}Ce projet implémente un système complet de gestion de livraisons")
    print(f"utilisant Redis (temps réel) et MongoDB (historique/analyses).")
    print()
    print(f"Développé en Python avec:")
    print(f"  • Redis pour l'état temps réel")
    print(f"  • MongoDB pour l'historique et les analyses")
    print(f"  • Docker pour l'infrastructure")
    print(f"{Style.RESET_ALL}")


def display_menu():
    """Afficher le menu principal"""
    print(f"\n{Fore.YELLOW}{'─' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}MENU PRINCIPAL{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 80}{Style.RESET_ALL}")
    print()
    print("1. Partie 1 - État temps réel avec Redis")
    print("2. Partie 2 - Historique et analyses avec MongoDB")
    print("3. Partie 3 - Structures avancées")
    print("4. Partie 4 - Geo-spatial (localisation temps réel)")
    print("5. Exécuter TOUTES les parties")
    print("6. Tester les connexions")
    print("0. Quitter")
    print()


def test_connections():
    """Tester les connexions Redis et MongoDB"""
    print_header("TEST DES CONNEXIONS")
    
    # Test Redis
    r = get_redis_connection()
    if r:
        print_success("Redis: OK")
        info = r.info('server')
        print_info(f"  Version: {info.get('redis_version', 'N/A')}")
    else:
        print_error("Redis: ÉCHEC")
        print_info("  Assurez-vous que Docker est lancé: docker-compose up -d")
    
    # Test MongoDB
    db = get_mongodb_connection()
    if db:
        print_success("MongoDB: OK")
        try:
            server_info = db.client.server_info()
            print_info(f"  Version: {server_info.get('version', 'N/A')}")
        except:
            pass
    else:
        print_error("MongoDB: ÉCHEC")
        print_info("  Assurez-vous que Docker est lancé: docker-compose up -d")
    
    print()
    if r and db:
        print_success("✓ Toutes les connexions sont établies!")
        print_info("Vous pouvez exécuter les parties du projet.")
        return True
    else:
        print_error("✗ Certaines connexions ont échoué")
        print_info("Veuillez vérifier Docker et réessayer.")
        return False


def run_all_parts():
    """Exécuter toutes les parties du projet"""
    print_header("EXÉCUTION COMPLÈTE DU PROJET")
    
    print_info("Cette exécution va lancer toutes les parties du projet de manière séquentielle.")
    print_info("Vous pouvez appuyer sur Entrée à chaque étape pour continuer.\n")
    
    response = input(f"{Fore.YELLOW}Continuer? (o/n): {Style.RESET_ALL}")
    if response.lower() != 'o':
        print_info("Annulé.")
        return
    
    # Exécuter chaque partie
    parts = [
        ("Partie 1 - Redis temps réel", run_partie1),
        ("Partie 2 - MongoDB historique", run_partie2),
        ("Partie 3 - Structures avancées", run_partie3),
        ("Partie 4 - Geo-spatial", run_partie4),
    ]
    
    for i, (name, func) in enumerate(parts, 1):
        print(f"\n{'=' * 80}")
        print(f"{Fore.GREEN}Exécution de la {name}{Style.RESET_ALL}")
        print(f"{'=' * 80}\n")
        
        try:
            func()
        except Exception as e:
            print_error(f"Erreur lors de l'exécution de {name}: {e}")
            import traceback
            traceback.print_exc()
            
            response = input(f"\n{Fore.YELLOW}Continuer malgré l'erreur? (o/n): {Style.RESET_ALL}")
            if response.lower() != 'o':
                break
        
        if i < len(parts):
            print(f"\n{Fore.CYAN}{'─' * 80}{Style.RESET_ALL}")
            wait_for_input(f"Appuyez sur Entrée pour passer à la partie suivante...")
    
    print_header("PROJET TERMINÉ")
    print_success("✓ Toutes les parties ont été exécutées!")
    print_info("Vous pouvez consulter la documentation pour plus de détails.")


def main():
    """Fonction principale"""
    display_welcome()
    
    # Menu interactif
    while True:
        display_menu()
        
        try:
            choice = input(f"{Fore.YELLOW}Votre choix: {Style.RESET_ALL}").strip()
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Interruption utilisateur. Au revoir!{Style.RESET_ALL}")
            sys.exit(0)
        
        if not choice:
            continue
        
        if choice == '0':
            print(f"\n{Fore.CYAN}Au revoir!{Style.RESET_ALL}\n")
            break
        elif choice == '1':
            try:
                run_partie1()
            except Exception as e:
                print_error(f"Erreur: {e}")
                import traceback
                traceback.print_exc()
        elif choice == '2':
            try:
                run_partie2()
            except Exception as e:
                print_error(f"Erreur: {e}")
                import traceback
                traceback.print_exc()
        elif choice == '3':
            try:
                run_partie3()
            except Exception as e:
                print_error(f"Erreur: {e}")
                import traceback
                traceback.print_exc()
        elif choice == '4':
            try:
                run_partie4()
            except Exception as e:
                print_error(f"Erreur: {e}")
                import traceback
                traceback.print_exc()
        elif choice == '5':
            run_all_parts()
        elif choice == '6':
            test_connections()
        else:
            print_warning("Choix invalide. Veuillez réessayer.")
        
        # Petite pause avant d'afficher le menu à nouveau
        if choice != '0':
            wait_for_input("\nAppuyez sur Entrée pour retourner au menu...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Programme interrompu. Au revoir!{Style.RESET_ALL}\n")
        sys.exit(0)
