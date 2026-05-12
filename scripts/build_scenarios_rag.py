"""
Script de construction du RAG scénarios.
Charge les scénarios de référence, les vectorise
et les indexe dans ChromaDB.

Exécutable avec : python scripts/build_scenarios_rag.py
"""

import json
import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from rag.vectorstore import init_chromadb
from rag.embedder import get_embedder, embed_texts

# Charger les variables d'environnement
load_dotenv()


def build_scenario_text(scenario: dict) -> str:
    """
    Construit un texte descriptif complet à partir d'un scénario.

    Args:
        scenario: Dictionnaire du scénario de référence.

    Returns:
        str: Texte descriptif pour l'indexation.
    """
    h = scenario["hypotheses"]

    # Calculer le total des charges fixes (H13 à H18)
    total_charges = (
        h.get("H13_loyer", 0)
        + h.get("H14_salaires", 0)
        + h.get("H15_utilites", 0)
        + h.get("H16_licences", 0)
        + h.get("H17_marketing", 0)
        + h.get("H18_honoraires", 0)
    )

    texte = (
        f"Scénario entrepreneur marocain : {scenario['titre']}\n"
        f"Secteur : {scenario['secteur']} | Ville : {scenario['ville']}\n"
        f"Segment client : {h.get('H1_segment', '')}\n"
        f"Prix de vente : {h.get('H2_prix_vente', 0)} MAD\n"
        f"Clients mois 1 : {h.get('H4_clients_mois1', 0)}\n"
        f"Taux croissance : {h.get('H5_taux_croissance', 0)}%\n"
        f"Type activité : {h.get('H8_type_activite', '')}\n"
        f"Loyer mensuel : {h.get('H13_loyer', 0)} MAD\n"
        f"Salaires : {h.get('H14_salaires', 0)} MAD\n"
        f"Charges totales fixes : {total_charges} MAD\n"
        f"Résultat : {scenario['resultat_validation']}\n"
        f"Analyse : {scenario['note_pedagogique']}"
    )

    return texte


def main():
    """Construit le RAG scénarios à partir du fichier JSON."""

    # --- Chemins ---
    scenarios_path = os.path.join("data", "scenarios_reference.json")
    chroma_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")

    # --- Vérifier que le fichier existe ---
    if not os.path.exists(scenarios_path):
        print(f"❌ Erreur : fichier introuvable à '{scenarios_path}'")
        sys.exit(1)

    # --- Charger les scénarios ---
    print(f"📄 Chargement des scénarios : {scenarios_path}")
    with open(scenarios_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    print(f"   → {len(scenarios)} scénarios chargés")

    # --- Initialiser ChromaDB ---
    print(f"🗄️  Initialisation de ChromaDB : {chroma_path}")
    collection = init_chromadb(chroma_path)

    # --- Initialiser l'embedder ---
    print("🧠 Chargement du modèle d'embeddings (all-MiniLM-L6-v2)...")
    embedder = get_embedder()

    # --- Construire les textes descriptifs ---
    print("📝 Construction des textes descriptifs...")
    textes = []
    ids = []
    metadatas = []

    for scenario in scenarios:
        texte = build_scenario_text(scenario)
        textes.append(texte)
        ids.append(scenario["id"])
        metadatas.append({
            "type": "scenario_reference",
            "secteur": scenario["secteur"],
            "ville": scenario["ville"],
            "resultat": scenario["resultat_validation"],
            "source": "scenarios_maroc_2024",
        })

    # --- Vectoriser ---
    print("🔢 Vectorisation des scénarios...")
    embeddings = embed_texts(textes, embedder)

    # --- Indexer dans ChromaDB ---
    print("📥 Indexation dans ChromaDB...")
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=textes,
        metadatas=metadatas,
    )

    print(f"\n✅ Scénarios indexés : {len(scenarios)} scénarios ajoutés")


if __name__ == "__main__":
    main()
