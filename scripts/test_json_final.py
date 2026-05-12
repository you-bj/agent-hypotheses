"""
Script de test du JSON final.
Vérifie que construire_json_final() produit un JSON
valide et complet prêt pour l'Agent Finance.

Exécutable avec : python scripts/test_json_final.py
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.output_builder import construire_json_final
from agent.validation import valider_toutes_hypotheses


def main():
    """Teste la construction du JSON final avec des hypothèses de test."""

    # --- Hypothèses de test (épicerie en ligne Tanger) ---
    hypotheses_test = {
        "segment_client": "B2C",
        "prix_vente_unitaire": 150,
        "abonnement_mensuel": 0,
        "nb_clients_mois1": 30,
        "taux_croissance_mensuel": 10,
        "taux_fidelisation": 70,
        "saisonnalite": "Ramadan fort, été faible",
        "type_activite": "produit",
        "cout_fabrication_unitaire": 80,
        "quantite_min_commande": 100,
        "cout_infra_numerique": 200,
        "delai_fournisseur_jours": 7,
        "loyer_mensuel": 3000,
        "salaires_equipe": 6000,
        "charges_utilites": 500,
        "licences_logicielles": 200,
        "budget_marketing": 1000,
        "honoraires_conseil": 500,
        "investissements_initiaux": 15000,
        "certifications": 0,
        "emprunts": 0,
        "nature_clients_encaissements": "B2C",
    }

    description_projet = "Je veux créer une épicerie en ligne à Tanger"

    # --- Mapper pour la validation (attend H2_prix_vente, etc.) ---
    hypotheses_pour_validation = {
        "H2_prix_vente": hypotheses_test["prix_vente_unitaire"],
        "H4_clients_mois1": hypotheses_test["nb_clients_mois1"],
        "H5_taux_croissance": hypotheses_test["taux_croissance_mensuel"],
        "H8_type_activite": hypotheses_test["type_activite"],
        "H9_cout_fabrication": hypotheses_test["cout_fabrication_unitaire"],
        "H13_loyer": hypotheses_test["loyer_mensuel"],
        "H14_salaires": hypotheses_test["salaires_equipe"],
        "H15_utilites": hypotheses_test["charges_utilites"],
        "H16_licences": hypotheses_test["licences_logicielles"],
        "H17_marketing": hypotheses_test["budget_marketing"],
        "H18_honoraires": hypotheses_test["honoraires_conseil"],
        "H19_investissements": hypotheses_test["investissements_initiaux"],
        "H21_emprunts": hypotheses_test["emprunts"],
    }

    # --- Validation ---
    print("🔄 Validation des hypothèses...")
    validation = valider_toutes_hypotheses(hypotheses_pour_validation)
    print(f"   Résultat : {validation['validation_globale']}")

    # --- Construction du JSON final ---
    print("🔄 Construction du JSON final...")
    json_final = construire_json_final(
        hypotheses_collectees=hypotheses_test,
        validation_globale=validation,
        description_projet=description_projet,
        questions_delegees=[],
    )

    # --- Afficher le JSON ---
    print("\n" + "=" * 60)
    print("📤 JSON FINAL COMPLET")
    print("=" * 60)
    print(json_final.model_dump_json(indent=2))

    # --- Vérification des champs obligatoires ---
    print("\n" + "=" * 60)
    print("🔍 VÉRIFICATION DES CHAMPS")
    print("=" * 60)

    champs_obligatoires = [
        "session_id", "timestamp", "description_projet",
        "bloc1_ventes", "bloc2_achats", "bloc3_charges",
        "bloc4_encaissements", "validation", "scenarios",
        "questions_delegees", "statut_global", "message_final",
    ]

    data = json_final.model_dump()
    tous_presents = True

    for champ in champs_obligatoires:
        if champ in data:
            print(f"  ✅ {champ}")
        else:
            print(f"  ❌ {champ} MANQUANT")
            tous_presents = False

    # --- Résultat ---
    print(f"\n{'=' * 60}")
    if tous_presents:
        print("✅ JSON final valide et prêt pour l'Agent Finance")
    else:
        print("❌ JSON final incomplet — champs manquants")
        sys.exit(1)

    print(f"\n📌 Session  : {json_final.session_id}")
    print(f"📌 Statut   : {json_final.statut_global}")
    print(f"📌 Message  : {json_final.message_final}")
    print("=" * 60)


if __name__ == "__main__":
    main()
