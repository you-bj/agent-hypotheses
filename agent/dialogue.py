"""
Module de dialogue de l'Agent Hypothèses.
Gère la conversation avec l'entrepreneur question par question,
valide les réponses via Groq et collecte les 22 hypothèses.
"""

import json
import re

from groq import Groq

from agent.questions import QUESTIONS
from agent.validation import valider_seuils, valider_toutes_hypotheses
from agent.output_builder import construire_json_final
from rag.retriever import search_context


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

def get_system_prompt() -> str:
    """
    Retourne le prompt système de l'agent.

    Returns:
        str: Le prompt système définissant le rôle de l'agent.
    """
    return (
        "Tu es un assistant pédagogique expert en création d'entreprise "
        "au Maroc. Tu aides les entrepreneurs à construire leur Business "
        "Plan en collectant leurs hypothèses financières. Tu poses une "
        "seule question à la fois, tu expliques pourquoi cette information "
        "est importante, et tu valides la réponse avant de passer à la "
        "suivante. Tu parles uniquement en français. Tu es bienveillant, "
        "clair et pédagogique. Quand une valeur semble irréaliste, tu le "
        "signales gentiment et tu demandes confirmation."
    )


def build_question_prompt(
    question_data: dict,
    contexte_chauvin: str,
    historique: list[dict],
) -> str:
    """
    Construit le prompt pour poser une question à l'entrepreneur.

    Args:
        question_data: Dictionnaire avec id, question, variable, type.
        contexte_chauvin: Texte retourné par le RAG.
        historique: Liste de messages {"role": ..., "content": ...}.

    Returns:
        str: Le prompt structuré à envoyer à Groq.
    """
    question_texte = question_data.get("question", "")
    question_id = question_data.get("id", "")

    prompt = (
        "Tu es un assistant qui collecte des hypothèses "
        "Business Plan. Tu dois poser UNE SEULE question "
        "à l'entrepreneur.\n\n"
        f"Question à poser : {question_texte}\n"
        f"Identifiant : {question_id}\n\n"
        "Instructions STRICTES :\n"
        "- Écris UNE phrase d'explication (maximum 20 mots) "
        "qui dit pourquoi cette information est importante\n"
        "- Ensuite pose la question telle quelle\n"
        "- NE PAS inventer d'autres questions\n"
        "- NE PAS demander de confirmation\n"
        "- NE PAS faire de validation dans ta réponse\n"
        "- NE PAS écrire plus de 3 lignes au total\n"
        "- STOP après la question\n\n"
        "Format de réponse obligatoire :\n"
        "[explication courte en une phrase]\n"
        "[question]"
    )

    return prompt


# ---------------------------------------------------------------------------
# Interaction avec Groq
# ---------------------------------------------------------------------------

def poser_question(
    client_groq: Groq,
    question_data: dict,
    contexte_chauvin: str,
    historique: list[dict],
) -> str:
    """
    Pose une question à l'entrepreneur via Groq.

    Args:
        client_groq: Instance du client Groq.
        question_data: Dictionnaire de la question courante.
        contexte_chauvin: Contexte RAG pertinent.
        historique: Historique de la conversation.

    Returns:
        str: Texte de la réponse de Groq.
    """
    prompt = build_question_prompt(question_data, contexte_chauvin, historique)

    reponse = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=150,
        stop=["Question suivante", "Validation", "Confirmation", "Réponse :"],
    )

    return reponse.choices[0].message.content


def valider_reponse_avec_groq(
    client_groq: Groq,
    question_data: dict,
    reponse_utilisateur: str,
    contexte_chauvin: str,
) -> dict:
    """
    Valide la réponse de l'entrepreneur via Groq.

    Args:
        client_groq: Instance du client Groq.
        question_data: Dictionnaire de la question courante.
        reponse_utilisateur: Réponse saisie par l'entrepreneur.
        contexte_chauvin: Contexte RAG pertinent.

    Returns:
        dict: Dictionnaire avec les clés :
            - valide (bool)
            - valeur_extraite (any)
            - message (str ou None)
    """
    question_texte = question_data.get("question", "")
    type_attendu = question_data.get("type", "")

    # Déterminer les options valides selon le type
    if type_attendu == "choix":
        # Extraire les options de la question entre parenthèses
        match_options = re.search(r'\(([^)]+)\)', question_texte)
        options = match_options.group(1) if match_options else "voir la question"
    else:
        options = "nombre positif"

    prompt = (
        f"Question posée : {question_texte}\n"
        f"Type attendu : {type_attendu}\n"
        f"Options valides : {options}\n"
        f"Réponse de l'entrepreneur : {reponse_utilisateur}\n\n"
        f"Analyse la réponse. Retourne UNIQUEMENT ce JSON :\n"
        f'{{"valide": true, "valeur_extraite": "valeur nettoyée en minuscules", '
        f'"message": null}}\n'
        f"ou\n"
        f'{{"valide": false, "valeur_extraite": null, '
        f'"message": "raison courte"}}\n\n'
        f"Règles strictes :\n"
        f"- Si type=choix : valide seulement si dans les options\n"
        f"- Si type=numerique ou pourcentage : valide si c'est un nombre >= 0\n"
        f"- Si type=booleen_details ou numerique_details : valide si non vide\n"
        f"- NE PAS écrire autre chose que le JSON\n"
        f"- NE PAS ajouter d'explication autour du JSON"
    )

    reponse = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un validateur de données. Tu retournes "
                    "UNIQUEMENT du JSON valide, sans aucun texte avant ou après."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=150,
    )

    texte_reponse = reponse.choices[0].message.content.strip()

    # Extraire le JSON de la réponse (au cas où Groq ajoute du texte autour)
    try:
        # Chercher un bloc JSON dans la réponse
        match = re.search(r'\{.*\}', texte_reponse, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            return json.loads(texte_reponse)
    except json.JSONDecodeError:
        # En cas d'échec de parsing, considérer la réponse comme valide
        return {
            "valide": True,
            "valeur_extraite": reponse_utilisateur,
            "message": None,
        }


# ---------------------------------------------------------------------------
# Détection d'intention et réponse aux questions
# ---------------------------------------------------------------------------

def detecter_intention(
    client_groq: Groq,
    reponse_utilisateur: str,
    question_data: dict,
) -> dict:
    """
    Détecte l'intention de l'entrepreneur dans sa réponse.

    Args:
        client_groq: Instance du client Groq.
        reponse_utilisateur: Texte saisi par l'entrepreneur.
        question_data: Dictionnaire de la question courante.

    Returns:
        dict: Dictionnaire avec les clés :
            - intention (str) : 'reponse', 'question', 'hors_sujet' ou 'vide'
            - contenu (str ou None) : texte extrait si intention=reponse
    """
    question_texte = question_data.get("question", "")

    prompt = (
        f"L'entrepreneur a écrit : \"{reponse_utilisateur}\"\n"
        f"La question posée était : \"{question_texte}\"\n\n"
        f"Analyse l'intention de l'entrepreneur.\n"
        f"Retourne UNIQUEMENT un JSON avec ce format exact :\n"
        f'{{"intention": "reponse", "contenu": "le texte extrait"}}\n'
        f"ou\n"
        f'{{"intention": "question", "contenu": null}}\n'
        f"ou\n"
        f'{{"intention": "hors_sujet", "contenu": null}}\n'
        f"ou\n"
        f'{{"intention": "vide", "contenu": null}}\n\n'
        f"Règles :\n"
        f"- 'reponse' : l'entrepreneur répond directement à la question\n"
        f"- 'question' : l'entrepreneur pose une question "
        f"(commence par pourquoi, comment, c'est quoi, qu'est-ce que, ?)\n"
        f"- 'hors_sujet' : réponse incompréhensible ou sans rapport\n"
        f"- 'vide' : réponse vide ou juste des espaces"
    )

    reponse = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un analyseur d'intention. Tu retournes "
                    "UNIQUEMENT du JSON valide, sans aucun texte avant ou après."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=150,
    )

    texte_reponse = reponse.choices[0].message.content.strip()

    try:
        match = re.search(r'\{.*\}', texte_reponse, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            return json.loads(texte_reponse)
    except json.JSONDecodeError:
        return {"intention": "reponse", "contenu": reponse_utilisateur}


def classifier_question(
    client_groq: Groq,
    question_utilisateur: str,
) -> dict:
    """
    Classifie une question de l'entrepreneur dans une catégorie
    pour le routage multi-agents.

    Args:
        client_groq: Instance du client Groq.
        question_utilisateur: Question posée par l'entrepreneur.

    Returns:
        dict: Dictionnaire avec les clés :
            - categorie (str) : 'chauvin', 'general', 'marche', 'finance' ou 'hors_sujet'
            - confiance (str) : 'haute', 'moyenne' ou 'basse'
    """
    prompt = (
        f"Un entrepreneur pose cette question pendant la "
        f"collecte de ses hypothèses Business Plan :\n"
        f"\"{question_utilisateur}\"\n\n"
        f"Classifie cette question dans une de ces catégories :\n\n"
        f"- 'chauvin' : question sur les hypothèses financières, "
        f"seuil de rentabilité, charges fixes, prix de vente, "
        f"clients, Business Plan, scénarios financiers\n\n"
        f"- 'general' : question sur les concepts de création "
        f"d'entreprise au Maroc (SARL, SA, Auto-entrepreneur, "
        f"TVA, CNSS, CRI, OMPIC, statuts juridiques, "
        f"démarches administratives)\n\n"
        f"- 'marche' : question sur le marché, la concurrence, "
        f"le secteur d'activité, la saturation du marché, "
        f"les tendances, les opportunités au Maroc\n\n"
        f"- 'finance' : question sur les calculs financiers "
        f"avancés (BFR, compte de résultat, plan de "
        f"financement, ratios financiers)\n\n"
        f"- 'hors_sujet' : question sans rapport avec la "
        f"création d'entreprise\n\n"
        f"Retourne UNIQUEMENT un JSON :\n"
        f'{{"categorie": "chauvin", "confiance": "haute"}}'
    )

    reponse = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un classificateur de questions. Tu retournes "
                    "UNIQUEMENT du JSON valide, sans aucun texte avant ou après."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=100,
    )

    texte_reponse = reponse.choices[0].message.content.strip()

    try:
        match = re.search(r'\{.*\}', texte_reponse, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            return json.loads(texte_reponse)
    except json.JSONDecodeError:
        return {"categorie": "chauvin", "confiance": "basse"}


def repondre_a_question_utilisateur(
    client_groq: Groq,
    question_utilisateur: str,
    contexte_chauvin: str,
    score_rag: int = 0,
):
    """
    Répond à une question posée par l'entrepreneur.

    Si le RAG a trouvé des résultats pertinents (score_rag > 0),
    répond directement avec le contexte Chauvin.
    Sinon, classifie la question et délègue à l'agent approprié.

    Args:
        client_groq: Instance du client Groq.
        question_utilisateur: Question posée par l'entrepreneur.
        contexte_chauvin: Contexte RAG pertinent.
        score_rag: Nombre de résultats pertinents trouvés dans ChromaDB.

    Returns:
        str: Réponse pédagogique si score_rag > 0.
        dict: Dictionnaire de délégation si la question doit être routée.
        None: Si la question est hors sujet.
    """
    # --- Cas 1 : Réponse trouvée dans Chauvin ---
    if score_rag > 0:
        prompt = (
            "Réponds en maximum 2 phrases simples et claires.\n"
            "NE PAS poser de questions supplémentaires.\n"
            "NE PAS faire de listes.\n\n"
            f"Question de l'entrepreneur : {question_utilisateur}\n"
            f"Contexte Chauvin disponible : {contexte_chauvin}"
        )

        reponse = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=200,
        )

        print("📖 Source : Chauvin")
        return reponse.choices[0].message.content

    # --- Cas 2 : Pas trouvé dans Chauvin → classifier ---
    classification = classifier_question(client_groq, question_utilisateur)
    categorie = classification.get("categorie", "hors_sujet")

    if categorie == "general":
        print(
            "💡 Cette question concerne la création "
            "d'entreprise au Maroc. L'agent spécialisé "
            "vous répondra. [EN ATTENTE - Agent Général]"
        )
        return {
            "deleger_a": "agent_general",
            "question": question_utilisateur,
            "status": "en_attente",
        }

    elif categorie == "marche":
        print(
            "💡 Cette question concerne l'analyse de marché. "
            "L'agent marché vous répondra. "
            "[EN ATTENTE - Agent Marché]"
        )
        return {
            "deleger_a": "agent_marche",
            "question": question_utilisateur,
            "status": "en_attente",
        }

    elif categorie == "finance":
        print(
            "💡 Cette question concerne les calculs financiers "
            "avancés. L'agent finance vous répondra. "
            "[EN ATTENTE - Agent Finance]"
        )
        return {
            "deleger_a": "agent_finance",
            "question": question_utilisateur,
            "status": "en_attente",
        }

    else:
        # categorie == 'hors_sujet' ou 'chauvin' sans résultat RAG
        print(
            "Je suis spécialisé dans la collecte des "
            "hypothèses de votre Business Plan. Je ne "
            "peux pas répondre à cette question. "
            "Revenons à nos hypothèses."
        )
        return None


# ---------------------------------------------------------------------------
# Hypothèses à passer automatiquement si activité = service
# ---------------------------------------------------------------------------

HYPOTHESES_SERVICE_SKIP = {"H9", "H10", "H12"}


# ---------------------------------------------------------------------------
# Dialogue principal
# ---------------------------------------------------------------------------

def conduire_dialogue(
    client_groq: Groq,
    collection_chroma,
    embedder,
    description_projet: str,
) -> dict:
    """
    Conduit le dialogue complet avec l'entrepreneur pour collecter
    les 22 hypothèses financières.

    Args:
        client_groq: Instance du client Groq.
        collection_chroma: Collection ChromaDB pour le RAG.
        embedder: Modèle SentenceTransformer pour les embeddings.
        description_projet: Description du projet de l'entrepreneur.

    Returns:
        dict: Dictionnaire contenant :
            - hypotheses (dict) : hypothèses collectées (variable → valeur)
            - questions_delegees (list) : questions routées vers d'autres agents
    """
    hypotheses_collectees = {}
    historique = []
    questions_delegees = []

    print("\n" + "=" * 60)
    print("🤝 Bonjour ! Je vais vous aider à construire votre")
    print("   Business Plan. Commençons par quelques questions.")
    print("=" * 60)
    print(f"\n📋 Projet : {description_projet}\n")

    # Noms affichables des blocs
    noms_blocs = {
        "bloc1_ventes": "📊 Bloc 1 — Ventes",
        "bloc2_achats": "🛒 Bloc 2 — Achats",
        "bloc3_charges": "💰 Bloc 3 — Charges fixes",
        "bloc4_encaissements": "🏦 Bloc 4 — Encaissements",
    }

    for nom_bloc, questions_bloc in QUESTIONS.items():
        print("\n" + "-" * 60)
        print(f"\n{noms_blocs.get(nom_bloc, nom_bloc)}\n")
        print("-" * 60)

        for question_data in questions_bloc:
            question_id = question_data["id"]
            variable = question_data["variable"]
            question_texte = question_data.get("question", "")

            # --- Skip automatique pour activité de type "service" ---
            if question_id in HYPOTHESES_SERVICE_SKIP:
                type_activite = hypotheses_collectees.get("type_activite", "")
                if isinstance(type_activite, str) and type_activite.lower() == "service":
                    hypotheses_collectees[variable] = 0
                    print(f"\n⏭️  {question_id} — Passée automatiquement "
                          f"(activité de type service). Valeur = 0")
                    continue

            # --- Boucle de validation avec détection d'intention ---
            tentatives = 0
            question_repondue = False

            while not question_repondue and tentatives < 3:

                # --- Chercher le contexte RAG ---
                try:
                    passages = search_context(
                        question_texte, collection_chroma, embedder, n_results=3
                    )
                    contexte_chauvin = "\n".join(passages) if passages else "Aucun contexte disponible."
                except Exception:
                    contexte_chauvin = "Aucun contexte disponible."

                # --- Poser la question via Groq ---
                print(f"\n🤖 [{question_id}]")
                if tentatives > 0:
                    print(f"⚠️  Tentative {tentatives + 1}/3")

                reponse_agent = poser_question(
                    client_groq, question_data, contexte_chauvin, historique
                )
                print(f"\n{reponse_agent}")

                # Ajouter la réponse de l'agent dans l'historique
                historique.append({
                    "role": "assistant",
                    "content": reponse_agent,
                })

                # --- Lire la réponse de l'utilisateur ---
                reponse_utilisateur = input("\n👤 Votre réponse : ").strip()

                # --- Gérer les réponses vides ---
                if not reponse_utilisateur:
                    print("Merci de répondre à la question pour continuer.")
                    tentatives += 1
                    continue

                # --- Détecter l'intention ---
                intention_result = detecter_intention(
                    client_groq, reponse_utilisateur, question_data
                )
                intention = intention_result.get("intention", "reponse")

                # --- Traitement selon l'intention ---

                if intention == "question":
                    # L'entrepreneur pose une question → y répondre
                    try:
                        passages_q = search_context(
                            reponse_utilisateur, collection_chroma, embedder, n_results=3
                        )
                        contexte_q = "\n".join(passages_q) if passages_q else "Aucun contexte disponible."
                        score_rag_q = len(passages_q)
                    except Exception:
                        contexte_q = "Aucun contexte disponible."
                        score_rag_q = 0

                    resultat = repondre_a_question_utilisateur(
                        client_groq, reponse_utilisateur, contexte_q,
                        score_rag=score_rag_q,
                    )

                    if isinstance(resultat, dict) and resultat.get("status") == "en_attente":
                        # Question déléguée à un autre agent
                        questions_delegees.append(resultat)
                    elif isinstance(resultat, str):
                        print(f"\n💡 {resultat}")
                    # Si None → hors sujet, déjà affiché

                    print("\nRevenons à notre question...")
                    # Ne pas incrémenter tentatives, reposer la question
                    continue

                elif intention == "hors_sujet":
                    print("Je n'ai pas compris votre réponse. "
                          "Pouvez-vous répondre directement à la question ?")
                    # Ne pas incrémenter tentatives, reposer la question
                    continue

                else:
                    # intention == 'reponse' (ou fallback)
                    # Ajouter la réponse utilisateur dans l'historique
                    historique.append({
                        "role": "user",
                        "content": reponse_utilisateur,
                    })

                    # --- Validation des seuils AVANT Groq ---
                    seuil_result = valider_seuils(
                        question_id, reponse_utilisateur
                    )

                    if seuil_result["status"] == "ERREUR":
                        print(f"❌ {seuil_result['message']}")
                        tentatives += 1
                        continue

                    if seuil_result["status"] == "AVERTISSEMENT":
                        print(f"⚠️  {seuil_result['message']}")
                        confirmation = input(
                            "Confirmez-vous cette valeur ? (oui/non) : "
                        ).strip().lower()
                        if confirmation != "oui":
                            continue

                    # --- Valider la réponse avec Groq ---
                    validation = valider_reponse_avec_groq(
                        client_groq, question_data, reponse_utilisateur, contexte_chauvin
                    )

                    if validation.get("valide", False):
                        valeur = validation.get("valeur_extraite", reponse_utilisateur)
                        hypotheses_collectees[variable] = valeur
                        print(f"✅ Enregistré : {variable} = {valeur}")
                        question_repondue = True
                    else:
                        message_erreur = validation.get("message", "Réponse invalide.")
                        print(f"⚠️  {message_erreur}")
                        tentatives += 1

            # --- Si 3 tentatives échouées ---
            if not question_repondue:
                hypotheses_collectees[variable] = None
                print(f"⏭️  Question ignorée après 3 tentatives. "
                      f"Vous pourrez la compléter plus tard.")

    print("\n" + "=" * 60)
    print("🎉 Collecte des hypothèses terminée !")
    print("=" * 60)

    # --- Validation globale des hypothèses ---
    print("\n" + "=" * 60)
    print("📊 VALIDATION GLOBALE DES HYPOTHÈSES")
    print("=" * 60)

    resultat_validation = valider_toutes_hypotheses(hypotheses_collectees)

    regles_noms = {
        "seuil_rentabilite": "Seuil de rentabilité",
        "symetrie_financement": "Symétrie de financement",
        "coherence_prix": "Cohérence prix / fabrication",
    }

    for cle, nom in regles_noms.items():
        r = resultat_validation[cle]
        status = r["status"]

        if status == "OK":
            emoji = "✅"
        elif status == "AVERTISSEMENT":
            emoji = "⚠️"
        else:
            emoji = "❌"

        print(f"\n{emoji} {nom} : {status}")
        if r.get("message"):
            print(f"   → {r['message']}")

    print(f"\n{'─' * 60}")
    print(f"Résultat global : {resultat_validation['validation_globale']}")
    print(f"Alertes : {resultat_validation['nb_alertes']} | "
          f"Erreurs : {resultat_validation['nb_erreurs']}")

    # --- Génération du JSON final ---
    json_final = construire_json_final(
        hypotheses_collectees=hypotheses_collectees,
        validation_globale=resultat_validation,
        description_projet=description_projet,
        questions_delegees=questions_delegees,
    )

    print("\n" + "=" * 60)
    print("📤 JSON FINAL GÉNÉRÉ POUR L'AGENT FINANCE")
    print("=" * 60)
    print(json_final.model_dump_json(indent=2))

    return {
        "hypotheses": hypotheses_collectees,
        "validation_globale": resultat_validation,
        "questions_delegees": questions_delegees,
        "json_final": json_final.model_dump(),
    }
