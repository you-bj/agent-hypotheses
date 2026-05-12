"""
Module de chargement du modèle d'embeddings
sentence-transformers pour la vectorisation des textes.
"""

from sentence_transformers import SentenceTransformer


def get_embedder() -> SentenceTransformer:
    """
    Charge et retourne un modèle d'embeddings sentence-transformers.
    Utilise le modèle all-MiniLM-L6-v2 (léger et performant).

    Returns:
        SentenceTransformer: Instance du modèle d'embeddings.
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


def embed_texts(texts: list[str], embedder: SentenceTransformer) -> list[list[float]]:
    """
    Vectorise une liste de textes avec le modèle d'embeddings.

    Args:
        texts: Liste de chaînes de caractères à vectoriser.
        embedder: Instance du modèle SentenceTransformer.

    Returns:
        list[list[float]]: Liste de vecteurs (un vecteur par texte).
    """
    return embedder.encode(texts).tolist()
