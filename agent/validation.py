"""
Module de validation des hypothèses selon les règles de Chauvin.
Contient les seuils par variable, la validation de rentabilité,
la symétrie de financement et la cohérence prix/fabrication.
"""

import math


# ---------------------------------------------------------------------------
# Seuils par variable
# ---------------------------------------------------------------------------

SEUILS_VARIABLES = {
    "H2": {
        "min": 1,
        "max": 500000,
        "message_min": "Le prix de vente doit être supérieur à 0 MAD.",
        "message_max": (
            "Un prix supérieur à 500 000 MAD semble très élevé. "
            "Confirmez-vous ?"
        ),
    },
    "H3": {
        "min": 0,
        "max": 100000,
        "message_min": "L'abonnement ne peut pas être négatif.",
        "message_max": (
            "Un abonnement supérieur à 100 000 MAD/mois semble très élevé."
        ),
    },
    "H4": {
        "min": 1,
        "max": 10000,
        "message_min": "Vous devez prévoir au moins 1 client pour démarrer.",
        "message_max": (
            "10 000 clients le premier mois est très ambitieux. "
            "Est-ce réaliste ?"
        ),
    },
    "H5": {
        "min": 0,
        "max": 100,
        "message_min": "Le taux de croissance ne peut pas être négatif.",
        "message_max": (
            "Un taux de croissance supérieur à 100% par mois est irréaliste. "
            "Valeur typique : 5% à 30%."
        ),
    },
    "H6": {
        "min": 0,
        "max": 100,
        "message_min": "Le taux de fidélisation ne peut pas être négatif.",
        "message_max": "Le taux de fidélisation ne peut pas dépasser 100%.",
    },
    "H9": {
        "min": 0,
        "max": 1000000,
        "message_min": "Le coût de fabrication ne peut pas être négatif.",
        "message_max": "Coût de fabrication très élevé. Vérifiez cette valeur.",
    },
    "H10": {
        "min": 0,
        "max": 1000000,
        "message_min": "La quantité minimum ne peut pas être négative.",
        "message_max": (
            "Quantité minimum très élevée. "
            "Vérifiez avec votre fournisseur."
        ),
    },
    "H11": {
        "min": 0,
        "max": 100000,
        "message_min": "Le coût infrastructure ne peut pas être négatif.",
        "message_max": (
            "Infrastructure supérieure à 100 000 MAD/mois semble très élevée."
        ),
    },
    "H12": {
        "min": 0,
        "max": 365,
        "message_min": "Le délai ne peut pas être négatif.",
        "message_max": "Un délai supérieur à 365 jours est irréaliste.",
    },
    "H13": {
        "min": 0,
        "max": 200000,
        "message_min": "Le loyer ne peut pas être négatif.",
        "message_max": (
            "Un loyer supérieur à 200 000 MAD/mois est très élevé "
            "pour le Maroc."
        ),
    },
    "H14": {
        "min": 0,
        "max": 1000000,
        "message_min": "Les salaires ne peuvent pas être négatifs.",
        "message_max": "Masse salariale très élevée. Vérifiez le total.",
    },
    "H15": {
        "min": 0,
        "max": 50000,
        "message_min": "Les charges ne peuvent pas être négatives.",
        "message_max": (
            "Charges d'utilités très élevées pour une TPE marocaine."
        ),
    },
    "H16": {
        "min": 0,
        "max": 50000,
        "message_min": "Les licences ne peuvent pas être négatives.",
        "message_max": (
            "Licences supérieures à 50 000 MAD/mois semblent très élevées."
        ),
    },
    "H17": {
        "min": 0,
        "max": 100000,
        "message_min": "Le budget marketing ne peut pas être négatif.",
        "message_max": "Budget marketing très élevé pour un démarrage.",
    },
    "H18": {
        "min": 0,
        "max": 100000,
        "message_min": "Les honoraires ne peuvent pas être négatifs.",
        "message_max": "Honoraires annuels très élevés.",
    },
    "H19": {
        "min": 0,
        "max": 10000000,
        "message_min": "Les investissements ne peuvent pas être négatifs.",
        "message_max": (
            "Investissement supérieur à 10 millions MAD. "
            "Vérifiez ce montant."
        ),
    },
    "H20": {
        "min": 0,
        "max": 500000,
        "message_min": "Les certifications ne peuvent pas être négatives.",
        "message_max": "Coût certifications très élevé.",
    },
}


# ---------------------------------------------------------------------------
# SMIG Maroc
# ---------------------------------------------------------------------------

SMIG_MAROC = 3111  # MAD/mois 2024


# ---------------------------------------------------------------------------
# Fonctions de validation
# ---------------------------------------------------------------------------

def valider_seuils(variable_id: str, valeur) -> dict:
    """
    Vérifie qu'une valeur respecte les seuils min/max définis
    pour la variable donnée.

    Args:
        variable_id: Identifiant de la variable (ex: "H2", "H13").
        valeur: Valeur saisie par l'entrepreneur.

    Returns:
        dict: {"status": ..., "niveau": "seuil", "message": ...}
    """
    seuil = SEUILS_VARIABLES.get(variable_id)

    if not seuil:
        return {"status": "OK", "niveau": "seuil", "message": None}

    try:
        valeur_num = float(valeur)
    except (ValueError, TypeError):
        return {"status": "OK", "niveau": "seuil", "message": None}

    if valeur_num < seuil["min"]:
        return {
            "status": "ERREUR",
            "niveau": "seuil",
            "message": seuil["message_min"],
        }

    if valeur_num > seuil["max"]:
        return {
            "status": "AVERTISSEMENT",
            "niveau": "seuil",
            "message": seuil["message_max"],
        }

    return {"status": "OK", "niveau": "seuil", "message": None}


def valider_salaires(salaires_total: float, nb_employes: int) -> dict:
    """
    Vérifie que le salaire moyen respecte le SMIG marocain.

    Args:
        salaires_total: Masse salariale mensuelle totale en MAD.
        nb_employes: Nombre d'employés.

    Returns:
        dict: {"status": ..., "niveau": "metier", "message": ...}
    """
    if nb_employes <= 0:
        return {"status": "OK", "niveau": "metier", "message": None}

    salaire_moyen = salaires_total / nb_employes

    if salaire_moyen < SMIG_MAROC:
        return {
            "status": "ERREUR",
            "niveau": "metier",
            "message": (
                f"Le salaire moyen de {salaire_moyen:.0f} MAD est inférieur "
                f"au SMIG marocain de {SMIG_MAROC} MAD/mois."
            ),
        }

    return {"status": "OK", "niveau": "metier", "message": None}


def valider_seuil_rentabilite(hypotheses_dict: dict) -> dict:
    """
    Calcule et valide le seuil de rentabilité selon Chauvin.

    Args:
        hypotheses_dict: Dictionnaire des hypothèses collectées.

    Returns:
        dict: Résultat de validation avec charges, CA, marge et seuil.
    """
    h = hypotheses_dict

    charges_fixes = (
        _safe_float(h.get("H13_loyer", 0))
        + _safe_float(h.get("H14_salaires", 0))
        + _safe_float(h.get("H15_utilites", 0))
        + _safe_float(h.get("H16_licences", 0))
        + _safe_float(h.get("H17_marketing", 0))
        + _safe_float(h.get("H18_honoraires", 0)) / 12
    )

    prix_vente = _safe_float(h.get("H2_prix_vente", 0))
    cout_fabrication = _safe_float(h.get("H9_cout_fabrication", 0))
    clients_mois1 = _safe_float(h.get("H4_clients_mois1", 0))

    marge_unitaire = prix_vente - cout_fabrication

    if marge_unitaire <= 0:
        return {
            "status": "ERREUR",
            "niveau": "chauvin",
            "charges_fixes_mensuelles": round(charges_fixes, 2),
            "ca_estime_mois1": 0,
            "marge_unitaire": round(marge_unitaire, 2),
            "seuil_clients_minimum": None,
            "message": (
                "Votre prix de vente est inférieur à votre coût de "
                "fabrication. Vous perdez de l'argent à chaque vente."
            ),
        }

    ca_estime_mois1 = prix_vente * clients_mois1
    seuil_clients = math.ceil(charges_fixes / marge_unitaire)

    if clients_mois1 >= seuil_clients:
        status = "OK"
        suffixe = " ✅ Objectif atteignable."
    else:
        status = "AVERTISSEMENT"
        suffixe = " ⚠️ Objectif insuffisant au démarrage."

    message = (
        f"Vos charges fixes sont de {charges_fixes:.0f} MAD/mois. "
        f"Avec une marge de {marge_unitaire:.0f} MAD par vente, "
        f"vous devez réaliser au minimum {seuil_clients} ventes "
        f"par mois pour couvrir vos charges. "
        f"Vous prévoyez {int(clients_mois1)} clients au mois 1."
        + suffixe
    )

    return {
        "status": status,
        "niveau": "chauvin",
        "charges_fixes_mensuelles": round(charges_fixes, 2),
        "ca_estime_mois1": round(ca_estime_mois1, 2),
        "marge_unitaire": round(marge_unitaire, 2),
        "seuil_clients_minimum": seuil_clients,
        "message": message,
    }


def valider_symetrie_financement(hypotheses_dict: dict) -> dict:
    """
    Valide la symétrie de financement selon Chauvin.

    Args:
        hypotheses_dict: Dictionnaire des hypothèses collectées.

    Returns:
        dict: {"status": ..., "niveau": "chauvin", "message": ...}
    """
    investissements = _safe_float(hypotheses_dict.get("H19_investissements", 0))
    emprunts = _safe_float(hypotheses_dict.get("H21_emprunts", 0))

    apports_propres = investissements - emprunts

    if apports_propres <= 0:
        return {
            "status": "ERREUR",
            "niveau": "chauvin",
            "message": (
                "Vos emprunts couvrent la totalité de vos investissements. "
                "Aucun apport personnel détecté."
            ),
        }

    if investissements > 2 * apports_propres:
        return {
            "status": "AVERTISSEMENT",
            "niveau": "chauvin",
            "message": (
                f"Selon Chauvin, vos besoins de financement "
                f"({investissements:.0f} MAD) dépassent le double de vos "
                f"apports personnels ({apports_propres:.0f} MAD). "
                f"Réfléchissez à réduire vos investissements initiaux "
                f"ou à trouver des associés."
            ),
        }

    return {"status": "OK", "niveau": "chauvin", "message": None}


def valider_coherence_prix_fabrication(hypotheses_dict: dict) -> dict:
    """
    Vérifie la cohérence entre prix de vente et coût de fabrication.

    Args:
        hypotheses_dict: Dictionnaire des hypothèses collectées.

    Returns:
        dict: {"status": ..., "niveau": "chauvin", "message": ...}
    """
    type_activite = str(hypotheses_dict.get("H8_type_activite", "")).lower()

    if type_activite == "service":
        return {"status": "OK", "niveau": "chauvin", "message": None}

    prix_vente = _safe_float(hypotheses_dict.get("H2_prix_vente", 0))
    cout_fabrication = _safe_float(hypotheses_dict.get("H9_cout_fabrication", 0))

    if prix_vente <= 0:
        return {"status": "OK", "niveau": "chauvin", "message": None}

    ratio = cout_fabrication / prix_vente

    if ratio > 0.8:
        return {
            "status": "AVERTISSEMENT",
            "niveau": "chauvin",
            "message": (
                "Votre coût de fabrication représente plus de 80% de "
                "votre prix de vente. Votre marge est très faible. "
                "Envisagez d'augmenter votre prix ou de réduire vos coûts."
            ),
        }

    return {"status": "OK", "niveau": "chauvin", "message": None}


# ---------------------------------------------------------------------------
# Validation globale
# ---------------------------------------------------------------------------

def valider_toutes_hypotheses(hypotheses_dict: dict) -> dict:
    """
    Exécute toutes les validations métier sur les hypothèses collectées.

    Args:
        hypotheses_dict: Dictionnaire des hypothèses collectées.

    Returns:
        dict: Résultats de toutes les validations avec résumé global.
    """
    resultat_rentabilite = valider_seuil_rentabilite(hypotheses_dict)
    resultat_financement = valider_symetrie_financement(hypotheses_dict)
    resultat_coherence = valider_coherence_prix_fabrication(hypotheses_dict)

    resultats = [resultat_rentabilite, resultat_financement, resultat_coherence]

    nb_alertes = sum(1 for r in resultats if r["status"] == "AVERTISSEMENT")
    nb_erreurs = sum(1 for r in resultats if r["status"] == "ERREUR")

    if nb_erreurs > 0:
        validation_globale = "ERREURS"
    elif nb_alertes > 0:
        validation_globale = "AVERTISSEMENTS"
    else:
        validation_globale = "OK"

    return {
        "seuil_rentabilite": resultat_rentabilite,
        "symetrie_financement": resultat_financement,
        "coherence_prix": resultat_coherence,
        "nb_alertes": nb_alertes,
        "nb_erreurs": nb_erreurs,
        "validation_globale": validation_globale,
    }


# ---------------------------------------------------------------------------
# Utilitaire
# ---------------------------------------------------------------------------

def _safe_float(valeur) -> float:
    """Convertit une valeur en float, retourne 0.0 en cas d'erreur."""
    try:
        return float(valeur)
    except (ValueError, TypeError):
        return 0.0
