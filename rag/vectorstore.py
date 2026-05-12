"""
Module d'initialisation du vector store ChromaDB
pour le stockage et la recherche des hypothèses de Chauvin.
"""

import os

import chromadb
from dotenv import load_dotenv

load_dotenv()


def init_chromadb(chroma_path: str) -> chromadb.Collection:
    """
    Initialise un client ChromaDB persistant et retourne
    la collection 'chauvin_hypotheses'.

    Args:
        chroma_path: Chemin vers le répertoire de stockage ChromaDB.

    Returns:
        chromadb.Collection: La collection 'chauvin_hypotheses' prête à l'emploi.
    """
    # Créer le dossier s'il n'existe pas
    os.makedirs(chroma_path, exist_ok=True)

    # Initialiser le client persistant
    client = chromadb.PersistentClient(path=chroma_path)

    # Créer ou récupérer la collection avec distance cosine
    collection = client.get_or_create_collection(
        name="chauvin_hypotheses",
        metadata={"hnsw:space": "cosine"},
    )

    return collection
