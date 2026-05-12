"""
Module de construction du JSON final des hypothèses.
Assemble les données collectées, la validation et les scénarios
en un objet Pydantic HypothesesOutput prêt pour l'Agent Finance.
"""

import uuid
from datetime import datetime

from schemas.output_schema import (
    Bloc1Ventes,
    Bloc2Achats,
    Bloc3Charges,
    Bloc4Encaissements,
    HypothesesOutput,
    QuestionDelegee,
    ResultatValidation,
    Scenario,
    TroisScenarios,
)
from agent.scenarios import generer_scenarios


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------

def _safe_float(valeur) -> float:
    """Convertit une valeur en float, retourne 0.0 en cas d'erreur."""
    try:
        return float(valeur)
    except (ValueError, TypeError):
        return 0.0


def determiner_regle_encaissement(nature_clients: str) -> dict:
    """
    Détermine la règle d'encaissement selon la nature des clients.

    Args:
        nature_clients: "B2C", "B2B" ou "Mixte".

    Returns:
        dict: {"regle": str, "delai": int}
    """
    nature = str(nature_clients).strip().lower()

    if nature == "b2c":
        return {"regle": "100% comptant", "delai": 0}
    elif nature == "b2b":
        return {"regle": "30 à 60 jours par défaut", "delai": 45}
    elif nature == "mixte":
        return {"regle": "Pondéré B2C/B2B", "delai": 20}
    else:
        return {"regle": "100% comptant", "delai": 0}


def determiner_message_final(
    validation_globale: str,
    nb_alertes: int,
    nb_erreurs: int,
    mois_rentabilite: int | None,
) -> str:
    """
    Génère un message final pédagogique selon les résultats.

    Args:
        validation_globale: "OK", "AVERTISSEMENTS" ou "ERREURS".
        nb_alertes: Nombre d'avertissements.
        nb_erreurs: Nombre d'erreurs.
        mois_rentabilite: Mois de rentabilité du scénario réaliste.

    Returns:
        str: Message final pour l'entrepreneur.
    """
    if nb_erreurs > 0:
        return (
            "Votre projet contient des incohérences à corriger "
            "avant de générer votre Business Plan."
        )

    if nb_alertes > 0 and mois_rentabilite and mois_rentabilite <= 12:
        return (
            "Votre projet est viable. Il sera rentable dans les "
            "12 premiers mois selon le scénario réaliste."
        )

    if nb_alertes > 0 and mois_rentabilite and mois_rentabilite <= 24:
        return (
            f"Votre projet est viable mais nécessite "
            f"{mois_rentabilite} mois avant rentabilité. "
            f"Assurez-vous d'avoir la trésorerie suffisante."
        )

    if nb_alertes > 0:
        return (
            "Votre projet nécessite une révision de ses hypothèses. "
            "La rentabilité n'est pas atteinte dans les 24 premiers mois."
        )

    return (
        "Excellent ! Votre projet est solide. "
        "Hypothèses cohérentes et rentabilité confirmée."
    )


# ---------------------------------------------------------------------------
# Construction du JSON final
# ---------------------------------------------------------------------------

def construire_json_final(
    hypotheses_collectees: dict,
    validation_globale: dict,
    description_projet: str,
    questions_delegees: list,
) -> HypothesesOutput:
    """
    Construit l'objet HypothesesOutput complet à partir des données collectées.

    Args:
        hypotheses_collectees: Dictionnaire variable → valeur.
        validation_globale: Résultat de valider_toutes_hypotheses().
        description_projet: Description du projet de l'entrepreneur.
        questions_delegees: Liste des questions déléguées aux autres agents.

    Returns:
        HypothesesOutput: Objet Pydantic prêt à être sérialisé en JSON.
    """
    h = hypotheses_collectees

    # --- Blocs d'hypothèses ---
    bloc1 = Bloc1Ventes(
        H1_segment_client=h.get("segment_client"),
        H2_prix_vente_unitaire=_safe_float(h.get("prix_vente_unitaire")),
        H3_abonnement_mensuel=_safe_float(h.get("abonnement_mensuel")),
        H4_nb_clients_mois1=_safe_float(h.get("nb_clients_mois1")),
        H5_taux_croissance_mensuel=_safe_float(h.get("taux_croissance_mensuel")),
        H6_taux_fidelisation=_safe_float(h.get("taux_fidelisation")),
        H7_saisonnalite=str(h.get("saisonnalite")) if h.get("saisonnalite") else None,
    )

    bloc2 = Bloc2Achats(
        H8_type_activite=h.get("type_activite"),
        H9_cout_fabrication_unitaire=_safe_float(h.get("cout_fabrication_unitaire")),
        H10_quantite_min_commande=_safe_float(h.get("quantite_min_commande")),
        H11_cout_infra_numerique=_safe_float(h.get("cout_infra_numerique")),
        H12_delai_fournisseur_jours=_safe_float(h.get("delai_fournisseur_jours")),
    )

    bloc3 = Bloc3Charges(
        H13_loyer_mensuel=_safe_float(h.get("loyer_mensuel")),
        H14_salaires_equipe=_safe_float(h.get("salaires_equipe")),
        H15_charges_utilites=_safe_float(h.get("charges_utilites")),
        H16_licences_logicielles=_safe_float(h.get("licences_logicielles")),
        H17_budget_marketing=_safe_float(h.get("budget_marketing")),
        H18_honoraires_conseil=_safe_float(h.get("honoraires_conseil")),
        H19_investissements_initiaux=_safe_float(h.get("investissements_initiaux")),
        H20_certifications=_safe_float(h.get("certifications")),
        H21_emprunts=_safe_float(h.get("emprunts")),
    )

    # --- Encaissements ---
    nature_clients = str(h.get("nature_clients_encaissements", "")).strip()
    regle = determiner_regle_encaissement(nature_clients)

    bloc4 = Bloc4Encaissements(
        H22_nature_clients=nature_clients if nature_clients else None,
        regle_defaut=regle["regle"],
        delai_jours=regle["delai"],
    )

    # --- Validation ---
    v = validation_globale
    sr = v.get("seuil_rentabilite", {})
    sf = v.get("symetrie_financement", {})
    cp = v.get("coherence_prix", {})

    resultat_val = ResultatValidation(
        seuil_rentabilite_status=sr.get("status", "OK"),
        seuil_rentabilite_message=sr.get("message", "") or "",
        charges_fixes_mensuelles=sr.get("charges_fixes_mensuelles"),
        marge_unitaire=sr.get("marge_unitaire"),
        seuil_clients_minimum=sr.get("seuil_clients_minimum"),
        symetrie_financement_status=sf.get("status", "OK"),
        symetrie_financement_message=sf.get("message", "") or "",
        coherence_prix_status=cp.get("status", "OK"),
        coherence_prix_message=cp.get("message", "") or "",
        nb_alertes=v.get("nb_alertes", 0),
        nb_erreurs=v.get("nb_erreurs", 0),
        validation_globale=v.get("validation_globale", "OK"),
    )

    # --- Scénarios ---
    # Mapper les clés pour generer_scenarios (attend H2_prix_vente, etc.)
    hypotheses_pour_scenarios = {
        "H2_prix_vente": _safe_float(h.get("prix_vente_unitaire")),
        "H4_clients_mois1": _safe_float(h.get("nb_clients_mois1")),
        "H5_taux_croissance": _safe_float(h.get("taux_croissance_mensuel")),
        "H9_cout_fabrication": _safe_float(h.get("cout_fabrication_unitaire")),
        "H13_loyer": _safe_float(h.get("loyer_mensuel")),
        "H14_salaires": _safe_float(h.get("salaires_equipe")),
        "H15_utilites": _safe_float(h.get("charges_utilites")),
        "H16_licences": _safe_float(h.get("licences_logicielles")),
        "H17_marketing": _safe_float(h.get("budget_marketing")),
        "H18_honoraires": _safe_float(h.get("honoraires_conseil")),
        "H19_investissements": _safe_float(h.get("investissements_initiaux")),
        "H20_certifications": _safe_float(h.get("certifications")),
    }

    scenarios_data = generer_scenarios(hypotheses_pour_scenarios)

    trois_scenarios = TroisScenarios(
        pessimiste=Scenario(**scenarios_data["pessimiste"]),
        realiste=Scenario(**scenarios_data["realiste"]),
        optimiste=Scenario(**scenarios_data["optimiste"]),
    )

    # --- Mois de rentabilité du scénario réaliste ---
    mois_rent = scenarios_data["realiste"].get("mois_rentabilite")

    # --- Message final ---
    message_final = determiner_message_final(
        validation_globale=v.get("validation_globale", "OK"),
        nb_alertes=v.get("nb_alertes", 0),
        nb_erreurs=v.get("nb_erreurs", 0),
        mois_rentabilite=mois_rent,
    )

    # --- Questions déléguées ---
    q_delegees = [
        QuestionDelegee(
            deleger_a=q.get("deleger_a", ""),
            question=q.get("question", ""),
            status=q.get("status", "en_attente"),
        )
        for q in questions_delegees
    ]

    # --- Construction finale ---
    return HypothesesOutput(
        session_id=str(uuid.uuid4())[:8],
        timestamp=datetime.now().isoformat(),
        description_projet=description_projet,
        bloc1_ventes=bloc1,
        bloc2_achats=bloc2,
        bloc3_charges=bloc3,
        bloc4_encaissements=bloc4,
        validation=resultat_val,
        scenarios=trois_scenarios,
        questions_delegees=q_delegees,
        statut_global=v.get("validation_globale", "OK"),
        message_final=message_final,
    )
