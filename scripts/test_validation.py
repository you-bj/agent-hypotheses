"""
Script de test de la validation et des scénarios.
Exécutable avec : python scripts/test_validation.py
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.validation import valider_toutes_hypotheses
from agent.scenarios import generer_scenarios


def main():
    """Teste la validation globale et la génération de scénarios."""

    # --- Hypothèses de test (épicerie en ligne Tanger) ---
    hypotheses_test = {
        "H2_prix_vente": 150,
        "H4_clients_mois1": 30,
        "H5_taux_croissance": 10,
        "H6_fidelisation": 70,
        "H8_type_activite": "produit",
        "H9_cout_fabrication": 80,
        "H13_loyer": 3000,
        "H14_salaires": 6000,
        "H15_utilites": 500,
        "H16_licences": 200,
        "H17_marketing": 1000,
        "H18_honoraires": 500,
        "H19_investissements": 15000,
        "H21_emprunts": 0,
    }

    # =============================================
    # VALIDATION
    # =============================================
    print("\n" + "=" * 60)
    print("📊 VALIDATION GLOBALE DES HYPOTHÈSES")
    print("=" * 60)

    resultat = valider_toutes_hypotheses(hypotheses_test)

    regles = {
        "seuil_rentabilite": "Seuil de rentabilité",
        "symetrie_financement": "Symétrie de financement",
        "coherence_prix": "Cohérence prix / fabrication",
    }

    for cle, nom in regles.items():
        r = resultat[cle]
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
    print(f"Résultat global : {resultat['validation_globale']}")
    print(f"Alertes : {resultat['nb_alertes']} | "
          f"Erreurs : {resultat['nb_erreurs']}")

    # =============================================
    # SCÉNARIOS
    # =============================================
    print("\n" + "=" * 60)
    print("📈 SCÉNARIOS FINANCIERS")
    print("=" * 60)

    scenarios = generer_scenarios(hypotheses_test)

    for nom, data in scenarios.items():
        print(f"\n{'─' * 40}")
        print(f"📌 {nom.upper()} (coef {data['coefficient']})")
        print(f"{'─' * 40}")
        print(f"   Clients mois 1     : {data['nb_clients_mois1']}")
        print(f"   CA mois 1          : {data['ca_mois1']:,.2f} MAD")
        print(f"   CA annuel          : {data['ca_annuel']:,.2f} MAD")
        print(f"   Charges annuelles  : {data['charges_annuelles']:,.2f} MAD")
        print(f"   Résultat net annuel: {data['resultat_net_annuel']:,.2f} MAD")

        if data["mois_rentabilite"]:
            print(f"   Mois rentabilité   : Mois {data['mois_rentabilite']}")
        else:
            print(f"   Mois rentabilité   : ❌ Non atteint en 24 mois")

        print(f"   → {data['interpretation']}")

    print(f"\n{'=' * 60}")
    print("✅ Validation et scénarios OK")
    print("=" * 60)


if __name__ == "__main__":
    main()
