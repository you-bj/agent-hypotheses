"""
Script de test du dialogue complet avec l'entrepreneur.
Exécutable avec : python scripts/test_dialogue.py
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from agent.groq_client import init_groq
from rag.vectorstore import init_chromadb
from rag.embedder import get_embedder
from agent.dialogue import conduire_dialogue

# Charger les variables d'environnement
load_dotenv()


def main():
    """Lance le dialogue complet de collecte des hypothèses."""

    try:
        # --- Initialisation ---
        print("🔄 Initialisation du client Groq...")
        client_groq = init_groq()

        chroma_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
        print(f"🗄️  Initialisation de ChromaDB ({chroma_path})...")
        collection = init_chromadb(chroma_path)

        print("🧠 Chargement du modèle d'embeddings...")
        embedder = get_embedder()

        # --- Lancer le dialogue ---
        description_projet = "Je veux créer une épicerie en ligne à Tanger"

        # --- Afficher les résultats ---
        resultat = conduire_dialogue(
            client_groq=client_groq,
            collection_chroma=collection,
            embedder=embedder,
            description_projet=description_projet,
        )

        hypotheses = resultat["hypotheses"]
        questions_delegees = resultat["questions_delegees"]
        validation = resultat.get("validation_globale", {})

        print("\n" + "=" * 60)
        print("📋 Récapitulatif des hypothèses collectées :")
        print("=" * 60)

        for variable, valeur in hypotheses.items():
            statut = "✅" if valeur is not None else "❌"
            print(f"  {statut} {variable} = {valeur}")

        nb_collectees = sum(1 for v in hypotheses.values() if v is not None)
        nb_total = len(hypotheses)

        print(f"\n✅ Dialogue terminé : {nb_collectees} hypothèses collectées "
              f"sur {nb_total}")

        # --- Afficher les questions déléguées ---
        if questions_delegees:
            print("\n" + "=" * 60)
            print("📤 Questions transmises aux autres agents :")
            print("=" * 60)

            for q in questions_delegees:
                print(f"  → [{q['deleger_a']}] {q['question']}")

            print(f"\n📤 {len(questions_delegees)} questions transmises "
                  f"aux autres agents")
        else:
            print("\n📤 0 questions transmises aux autres agents")

        # --- Afficher le résultat de validation ---
        if validation:
            print(f"\n📊 Validation globale : {validation.get('validation_globale', '?')}")
            print(f"   Alertes : {validation.get('nb_alertes', 0)} | "
                  f"Erreurs : {validation.get('nb_erreurs', 0)}")

        # --- Afficher le JSON final ---
        json_final = resultat.get("json_final")
        if json_final:
            print(f"\n📤 JSON final généré")
            print(f"   Session  : {json_final.get('session_id', '?')}")
            print(f"   Statut   : {json_final.get('statut_global', '?')}")
            print(f"   Message  : {json_final.get('message_final', '?')}")

    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
