"""
Module de génération de scénarios (pessimiste, réaliste, optimiste)
à partir des hypothèses collectées auprès de l'entrepreneur.
"""

import math


def calculer_ca_mensuel(hypotheses: dict, mois: int) -> float:
    """
    Calcule le chiffre d'affaires pour un mois donné.

    Le CA tient compte de la croissance mensuelle composée
    appliquée au nombre de clients du mois 1.

    Args:
        hypotheses: Dictionnaire des hypothèses.
        mois: Numéro du mois (1 = premier mois).

    Returns:
        float: CA du mois arrondi à 2 décimales.
    """
    prix_vente = _safe_float(hypotheses.get("H2_prix_vente", 0))
    clients_mois1 = _safe_float(hypotheses.get("H4_clients_mois1", 0))
    taux = _safe_float(hypotheses.get("H5_taux_croissance", 0)) / 100

    clients_mois = clients_mois1 * ((1 + taux) ** (mois - 1))
    ca = prix_vente * clients_mois

    return round(ca, 2)


def generer_scenarios(hypotheses_dict: dict) -> dict:
    """
    Génère 3 scénarios financiers à partir des hypothèses collectées.

    Coefficients :
        - pessimiste : 0.7 (30% moins de clients)
        - réaliste   : 1.0 (prévisions de l'entrepreneur)
        - optimiste  : 1.3 (30% plus de clients)

    Pour chaque scénario calcule : CA mois 1, CA annuel, charges
    annuelles, marge brute, résultat net, mois de rentabilité et
    détail du CA mensuel sur 12 mois.

    Args:
        hypotheses_dict: Dictionnaire des hypothèses collectées.

    Returns:
        dict: 3 clés (pessimiste, realiste, optimiste) avec
              les projections financières complètes.
    """
    h = hypotheses_dict

    prix_vente = _safe_float(h.get("H2_prix_vente", 0))
    clients_mois1 = _safe_float(h.get("H4_clients_mois1", 0))
    taux = _safe_float(h.get("H5_taux_croissance", 0)) / 100
    cout_fabrication = _safe_float(h.get("H9_cout_fabrication", 0))

    # Charges fixes mensuelles
    charges_fixes_mensuelles = (
        _safe_float(h.get("H13_loyer", 0))
        + _safe_float(h.get("H14_salaires", 0))
        + _safe_float(h.get("H15_utilites", 0))
        + _safe_float(h.get("H16_licences", 0))
        + _safe_float(h.get("H17_marketing", 0))
        + _safe_float(h.get("H18_honoraires", 0)) / 12
    )

    # Charges annuelles supplémentaires (investissement + certifications)
    charges_annuelles_sup = (
        _safe_float(h.get("H19_investissements", 0))
        + _safe_float(h.get("H20_certifications", 0))
    )

    coefficients = {
        "pessimiste": {
            "coef": 0.7,
            "interpretation": (
                "Scénario pessimiste: 30% moins de clients que prévu."
            ),
        },
        "realiste": {
            "coef": 1.0,
            "interpretation": (
                "Scénario réaliste: prévisions de l'entrepreneur."
            ),
        },
        "optimiste": {
            "coef": 1.3,
            "interpretation": (
                "Scénario optimiste: 30% plus de clients que prévu."
            ),
        },
    }

    scenarios = {}

    for nom, config in coefficients.items():
        coef = config["coef"]
        nb_clients_scenario = round(clients_mois1 * coef)

        # CA mensuel mois 1
        ca_mois1 = prix_vente * nb_clients_scenario

        # Détail du CA sur 12 mois et total annuel
        ca_12_mois = []
        ca_annuel = 0.0
        nb_ventes_annuelles = 0.0

        for mois in range(12):
            clients_mois = nb_clients_scenario * ((1 + taux) ** mois)
            ca_mois = prix_vente * clients_mois
            ca_12_mois.append(round(ca_mois, 2))
            ca_annuel += ca_mois
            nb_ventes_annuelles += clients_mois

        # Charges annuelles totales
        charges_annuelles = (charges_fixes_mensuelles * 12) + charges_annuelles_sup

        # Marge brute annuelle
        marge_brute_annuelle = ca_annuel - (cout_fabrication * nb_ventes_annuelles)

        # Résultat net annuel
        resultat_net_annuel = marge_brute_annuelle - charges_annuelles

        # Mois de rentabilité (premier mois où CA > charges fixes)
        mois_rentabilite = None
        marge_unitaire = prix_vente - cout_fabrication

        if marge_unitaire > 0:
            for m in range(1, 25):
                clients_m = nb_clients_scenario * ((1 + taux) ** (m - 1))
                marge_mois = marge_unitaire * clients_m
                if marge_mois >= charges_fixes_mensuelles:
                    mois_rentabilite = m
                    break

        scenarios[nom] = {
            "coefficient": coef,
            "nb_clients_mois1": nb_clients_scenario,
            "ca_mois1": round(ca_mois1, 2),
            "ca_annuel": round(ca_annuel, 2),
            "charges_annuelles": round(charges_annuelles, 2),
            "resultat_net_annuel": round(resultat_net_annuel, 2),
            "mois_rentabilite": mois_rentabilite,
            "ca_12_mois": ca_12_mois,
            "interpretation": config["interpretation"],
        }

    return scenarios


# ---------------------------------------------------------------------------
# Utilitaire
# ---------------------------------------------------------------------------

def _safe_float(valeur) -> float:
    """Convertit une valeur en float, retourne 0.0 en cas d'erreur."""
    try:
        return float(valeur)
    except (ValueError, TypeError):
        return 0.0
