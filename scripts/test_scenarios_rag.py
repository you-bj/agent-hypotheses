"""
Script de test du RAG scénarios.
Vérifie que les scénarios de référence sont bien
indexés et que la recherche fonctionne.

Exécutable avec : python scripts/test_scenarios_rag.py
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from rag.vectorstore import init_chromadb
from rag.embedder import get_embedder
from rag.retriever import search_scenarios

# Charger les variables d'environnement
load_dotenv()


def main():
    """Teste le RAG scénarios avec 3 recherches."""

    chroma_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")

    # --- Initialiser ---
    print("🗄️  Initialisation de ChromaDB...")
    collection = init_chromadb(chroma_path)

    print("🧠 Chargement du modèle d'embeddings...")
    embedder = get_embedder()

    # --- 3 recherches test ---
    queries = [
        "épicerie commerce alimentaire Tanger prix vente",
        "consultant service numérique charges faibles",
        "restaurant charges élevées risque rentabilité",
    ]

    tous_ok = True

    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 60}")
        print(f"🔍 Recherche {i} : \"{query}\"")
        print("=" * 60)

        resultats = search_scenarios(
            query=query,
            collection=collection,
            embedder=embedder,
            n_results=2,
        )

        if resultats:
            for j, res in enumerate(resultats, 1):
                texte = res["texte"]
                metadata = res["metadata"]
                resultat = metadata.get("resultat", "inconnu")

                # Extraire le titre (première ligne du texte)
                titre = texte.split("\n")[0] if texte else "Sans titre"

                emoji = "✅" if resultat == "viable" else "⚠️"
                print(f"\n  {emoji} Scénario {j} ({resultat}) :")
                print(f"     {titre}")
                print(f"     Secteur: {metadata.get('secteur', '?')} | "
                      f"Ville: {metadata.get('ville', '?')}")
        else:
            print("  ❌ Aucun scénario trouvé")
            tous_ok = False

    # --- Résultat final ---
    print(f"\n{'=' * 60}")
    if tous_ok:
        print("✅ Scénarios RAG fonctionnels")
    else:
        print("❌ Scénarios RAG vide - lance d'abord build_scenarios_rag.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
