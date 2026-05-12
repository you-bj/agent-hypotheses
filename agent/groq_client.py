"""
Module client Groq pour l'Agent Hypothèses.
Gère l'initialisation du client et la communication avec l'API Groq.
Toute la communication se fait uniquement en français.
"""

import os
import time

from dotenv import load_dotenv
from groq import Groq


def init_groq() -> Groq:
    """
    Initialise et retourne un client Groq.

    Charge la variable GROQ_API_KEY depuis le fichier .env
    et crée une instance du client Groq.

    Returns:
        Groq: Instance du client Groq configurée.

    Raises:
        ValueError: Si la clé API GROQ_API_KEY est absente ou vide.
    """
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "La clé API Groq est absente. "
            "Veuillez définir GROQ_API_KEY dans le fichier .env"
        )

    client = Groq(api_key=api_key)
    return client


def test_connexion(client: Groq) -> str:
    """
    Teste la connexion à Groq en envoyant un message simple.

    Envoie une requête au modèle llama-3.3-70b-versatile pour vérifier
    que la connexion fonctionne correctement.

    Args:
        client: Instance du client Groq initialisée.

    Returns:
        str: Le texte de la réponse du modèle.
    """
    debut = time.time()

    reponse = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un assistant pédagogique qui aide les entrepreneurs "
                    "marocains à créer leur Business Plan. Présente-toi en une "
                    "phrase simple."
                ),
            },
            {
                "role": "user",
                "content": "Présente-toi.",
            },
        ],
        temperature=0.7,
        max_tokens=150,
    )

    fin = time.time()
    temps_ms = round((fin - debut) * 1000)

    texte_reponse = reponse.choices[0].message.content
    print(f"⏱️  Temps de réponse : {temps_ms} ms")

    return texte_reponse
