"""
Tests unitaires pour l'Agent Hypothèses.
Couvre les fonctions de validation et la génération de scénarios.
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.validation import (
    valider_seuil_rentabilite,
    valider_symetrie_financement,
)
from agent.scenarios import generer_scenarios


# ---- Tests de valider_seuil_rentabilite ----

class TestValiderSeuilRentabilite:
    """Tests pour la fonction valider_seuil_rentabilite."""

    def test_seuil_rentabilite_ok(self):
        """CA supérieur aux charges fixes → statut OK."""
        resultat = valider_seuil_rentabilite(
            charges_fixes=5000, ca_estime=10000
        )
        assert resultat["status"] == "OK"
        assert "validé" in resultat["message"].lower()

    def test_seuil_rentabilite_alerte(self):
        """Charges fixes supérieures au CA → statut ALERTE."""
        resultat = valider_seuil_rentabilite(
            charges_fixes=15000, ca_estime=10000
        )
        assert resultat["status"] == "ALERTE"
        assert "risque" in resultat["message"].lower() or "attention" in resultat["message"].lower()

    def test_seuil_rentabilite_ca_zero(self):
        """CA estimé à zéro → statut ALERTE."""
        resultat = valider_seuil_rentabilite(
            charges_fixes=5000, ca_estime=0
        )
        assert resultat["status"] == "ALERTE"


# ---- Tests de valider_symetrie_financement ----

class TestValiderSymetrieFinancement:
    """Tests pour la fonction valider_symetrie_financement."""

    def test_symetrie_ok(self):
        """Apports >= 30% des besoins → statut OK."""
        resultat = valider_symetrie_financement(
            besoins_financement=100000, apports_personnels=40000
        )
        assert resultat["status"] == "OK"
        assert "validée" in resultat["message"].lower()

    def test_symetrie_alerte(self):
        """Apports < 30% des besoins → statut ALERTE."""
        resultat = valider_symetrie_financement(
            besoins_financement=100000, apports_personnels=10000
        )
        assert resultat["status"] == "ALERTE"
        assert "30%" in resultat["message"]

    def test_symetrie_besoins_zero(self):
        """Besoins de financement à zéro → statut ALERTE."""
        resultat = valider_symetrie_financement(
            besoins_financement=0, apports_personnels=5000
        )
        assert resultat["status"] == "ALERTE"


# ---- Tests de generer_scenarios ----

class TestGenererScenarios:
    """Tests pour la fonction generer_scenarios."""

    def test_scenarios_structure(self):
        """Vérifie que les 3 scénarios sont bien générés."""
        hypotheses = {
            "prix_vente_unitaire": 100,
            "nb_clients_mois1": 50,
            "taux_croissance_mensuel": 10,
        }
        scenarios = generer_scenarios(hypotheses)

        assert "pessimiste" in scenarios
        assert "realiste" in scenarios
        assert "optimiste" in scenarios

    def test_scenarios_coefficients(self):
        """Vérifie que les coefficients sont bien appliqués."""
        hypotheses = {
            "prix_vente_unitaire": 100,
            "nb_clients_mois1": 100,
            "taux_croissance_mensuel": 0,  # Pas de croissance pour simplifier
        }
        scenarios = generer_scenarios(hypotheses)

        assert scenarios["pessimiste"]["nb_clients_mois1"] == 70   # 100 * 0.7
        assert scenarios["realiste"]["nb_clients_mois1"] == 100    # 100 * 1.0
        assert scenarios["optimiste"]["nb_clients_mois1"] == 130   # 100 * 1.3

    def test_scenarios_ca_mensuel(self):
        """Vérifie le calcul du CA mensuel du mois 1."""
        hypotheses = {
            "prix_vente_unitaire": 200,
            "nb_clients_mois1": 50,
            "taux_croissance_mensuel": 5,
        }
        scenarios = generer_scenarios(hypotheses)

        # Scénario réaliste : 50 clients * 200 MAD = 10000 MAD
        assert scenarios["realiste"]["ca_mensuel_mois1"] == 10000
        # Scénario pessimiste : 35 clients * 200 MAD = 7000 MAD
        assert scenarios["pessimiste"]["ca_mensuel_mois1"] == 7000
