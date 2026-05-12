"""
Module de recherche contextuelle dans ChromaDB.
Permet de retrouver les passages pertinents liés
aux hypothèses de Chauvin.
"""

import chromadb
from sentence_transformers import SentenceTransformer


def search_context(
    query: str,
    collection: chromadb.Collection,
    embedder: SentenceTransformer,
    n_results: int = 3,
) -> list[str]:
    """
    Recherche les passages les plus pertinents dans la collection ChromaDB
    pour une requête donnée.

    Args:
        query: La requête textuelle de recherche.
        collection: La collection ChromaDB dans laquelle chercher.
        embedder: Instance du modèle SentenceTransformer pour vectoriser la query.
        n_results: Nombre de résultats à retourner (par défaut 3).

    Returns:
        list[str]: Liste des passages pertinents trouvés.
    """
    # Convertir la query en vecteur
    query_embedding = embedder.encode(query).tolist()

    # Chercher dans ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    # Extraire les documents depuis les résultats ChromaDB
    documents = results.get("documents", [[]])

    # Aplatir la liste (ChromaDB retourne une liste de listes)
    passages = []
    for doc_list in documents:
        for doc in doc_list:
            passages.append(doc)

    return passages


def search_scenarios(
    query: str,
    collection: chromadb.Collection,
    embedder: SentenceTransformer,
    secteur: str = None,
    n_results: int = 3,
) -> list[dict]:
    """
    Recherche les scénarios de référence les plus similaires dans ChromaDB.

    Filtre uniquement les documents avec metadata type = "scenario_reference".
    Si un secteur est fourni, filtre aussi par ce secteur.

    Args:
        query: La requête textuelle de recherche.
        collection: La collection ChromaDB dans laquelle chercher.
        embedder: Instance du modèle SentenceTransformer pour vectoriser la query.
        secteur: Secteur d'activité pour filtrer (optionnel).
        n_results: Nombre de résultats à retourner (par défaut 3).

    Returns:
        list[dict]: Liste de dictionnaires avec les clés :
            - texte (str) : texte du scénario
            - metadata (dict) : métadonnées associées
    """
    # Convertir la query en vecteur
    query_embedding = embedder.encode(query).tolist()

    # Construire le filtre de métadonnées
    if secteur:
        where_filter = {
            "$and": [
                {"type": {"$eq": "scenario_reference"}},
                {"secteur": {"$eq": secteur}},
            ]
        }
    else:
        where_filter = {"type": {"$eq": "scenario_reference"}}

    # Chercher dans ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter,
    )

    # Extraire les documents et métadonnées
    documents = results.get("documents", [[]])
    metadatas = results.get("metadatas", [[]])

    scenarios = []
    for doc_list, meta_list in zip(documents, metadatas):
        for doc, meta in zip(doc_list, meta_list):
            scenarios.append({
                "texte": doc,
                "metadata": meta,
            })

    return scenarios
