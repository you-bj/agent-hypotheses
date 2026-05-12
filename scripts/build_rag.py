"""
Script de construction du RAG.
Charge le PDF de Chauvin, le découpe en chunks, les vectorise
et les indexe dans ChromaDB.

Exécutable avec : python scripts/build_rag.py
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from rag.loader import load_pdf, chunk_text
from rag.vectorstore import init_chromadb
from rag.embedder import get_embedder, embed_texts

# Charger les variables d'environnement
load_dotenv()


def main():
    """Construit le RAG à partir du PDF de Chauvin."""

    # --- Chemins ---
    pdf_path = os.path.join("data", "raw", "chauvin.pdf")
    chroma_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")

    # --- Vérifier que le PDF existe ---
    if not os.path.exists(pdf_path):
        print(f"❌ Erreur : le fichier PDF est introuvable à '{pdf_path}'")
        print("   Placez le fichier chauvin.pdf dans le dossier data/raw/")
        sys.exit(1)

    # --- Charger le PDF ---
    print(f"📄 Chargement du PDF : {pdf_path}")
    pages = load_pdf(pdf_path)
    print(f"   → {len(pages)} pages extraites")

    # --- Découper en chunks ---
    print("✂️  Découpage en chunks...")
    chunks = chunk_text(pages, chunk_size=500, overlap=50)
    print(f"   → {len(chunks)} chunks créés")

    # --- Initialiser ChromaDB ---
    print(f"🗄️  Initialisation de ChromaDB : {chroma_path}")
    collection = init_chromadb(chroma_path)

    # --- Initialiser l'embedder ---
    print("🧠 Chargement du modèle d'embeddings (all-MiniLM-L6-v2)...")
    embedder = get_embedder()

    # --- Vectoriser les chunks ---
    print("🔢 Vectorisation des chunks...")
    textes = [chunk["text"] for chunk in chunks]
    embeddings = embed_texts(textes, embedder)

    # --- Indexer dans ChromaDB ---
    print("📥 Indexation dans ChromaDB...")
    collection.add(
        ids=[chunk["chunk_id"] for chunk in chunks],
        embeddings=embeddings,
        documents=[chunk["text"] for chunk in chunks],
        metadatas=[{"page": chunk["page"]} for chunk in chunks],
    )

    print(f"\n✅ RAG construit avec succès : {len(chunks)} chunks indexés")


if __name__ == "__main__":
    main()
