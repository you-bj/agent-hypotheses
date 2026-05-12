"""
Script de test de la connexion Groq.
Exécutable avec : python scripts/test_groq.py
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.groq_client import init_groq, test_connexion


def main():
    """Teste la connexion à l'API Groq et affiche le résultat."""
    try:
        print("🔄 Initialisation du client Groq...")
        client = init_groq()
        print("🔄 Test de connexion en cours...\n")

        reponse = test_connexion(client)

        print(f"\n💬 Réponse du modèle :\n{reponse}")
        print("\n✅ Connexion Groq OK")

    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
