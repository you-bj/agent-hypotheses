"""
Script de test du RAG.
Vérifie que ChromaDB contient des données et que la recherche fonctionne.

Exécutable avec : python scripts/test_rag.py
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from rag.vectorstore import init_chromadb
from rag.embedder import get_embedder
from rag.retriever import search_context

# Charger les variables d'environnement
load_dotenv()


def main():
    """Teste le RAG avec une requête de recherche."""

    chroma_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")

    # --- Initialiser ChromaDB et l'embedder ---
    print("🗄️  Initialisation de ChromaDB...")
    collection = init_chromadb(chroma_path)

    print("🧠 Chargement du modèle d'embeddings...")
    embedder = get_embedder()

    # --- Vérifier le nombre de documents indexés ---
    nb_docs = collection.count()
    print(f"📊 Documents indexés dans ChromaDB : {nb_docs}")

    if nb_docs == 0:
        print("\n❌ RAG vide - lance d'abord build_rag.py")
        sys.exit(1)

    # --- Recherche test ---
    query = "seuil de rentabilité charges fixes"
    print(f"\n🔍 Recherche : \"{query}\"")

    passages = search_context(query, collection, embedder, n_results=3)

    if passages:
        print(f"\n📋 {len(passages)} passage(s) trouvé(s) :\n")
        for i, passage in enumerate(passages, 1):
            print(f"--- Passage {i} ---")
            print(passage[:300])
            print()

        print("✅ RAG fonctionne")
    else:
        print("\n❌ RAG vide - lance d'abord build_rag.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
