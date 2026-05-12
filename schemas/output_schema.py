"""
Schéma Pydantic pour le JSON final des hypothèses
du Business Plan, incluant validation et scénarios.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Blocs d'hypothèses
# ---------------------------------------------------------------------------

class Bloc1Ventes(BaseModel):
    H1_segment_client: Optional[str] = None
    H2_prix_vente_unitaire: Optional[float] = None
    H3_abonnement_mensuel: Optional[float] = None
    H4_nb_clients_mois1: Optional[float] = None
    H5_taux_croissance_mensuel: Optional[float] = None
    H6_taux_fidelisation: Optional[float] = None
    H7_saisonnalite: Optional[str] = None


class Bloc2Achats(BaseModel):
    H8_type_activite: Optional[str] = None
    H9_cout_fabrication_unitaire: Optional[float] = None
    H10_quantite_min_commande: Optional[float] = None
    H11_cout_infra_numerique: Optional[float] = None
    H12_delai_fournisseur_jours: Optional[float] = None


class Bloc3Charges(BaseModel):
    H13_loyer_mensuel: Optional[float] = None
    H14_salaires_equipe: Optional[float] = None
    H15_charges_utilites: Optional[float] = None
    H16_licences_logicielles: Optional[float] = None
    H17_budget_marketing: Optional[float] = None
    H18_honoraires_conseil: Optional[float] = None
    H19_investissements_initiaux: Optional[float] = None
    H20_certifications: Optional[float] = None
    H21_emprunts: Optional[float] = None


class Bloc4Encaissements(BaseModel):
    H22_nature_clients: Optional[str] = None
    regle_defaut: Optional[str] = None
    delai_jours: Optional[int] = None


# ---------------------------------------------------------------------------
# Validation et scénarios
# ---------------------------------------------------------------------------

class ResultatValidation(BaseModel):
    seuil_rentabilite_status: str
    seuil_rentabilite_message: str
    charges_fixes_mensuelles: Optional[float] = None
    marge_unitaire: Optional[float] = None
    seuil_clients_minimum: Optional[int] = None
    symetrie_financement_status: str
    symetrie_financement_message: str
    coherence_prix_status: str
    coherence_prix_message: str
    nb_alertes: int
    nb_erreurs: int
    validation_globale: str


class Scenario(BaseModel):
    coefficient: float
    nb_clients_mois1: float
    ca_mois1: float
    ca_annuel: float
    charges_annuelles: float
    resultat_net_annuel: float
    mois_rentabilite: Optional[int] = None
    ca_12_mois: List[float]
    interpretation: str


class TroisScenarios(BaseModel):
    pessimiste: Scenario
    realiste: Scenario
    optimiste: Scenario


class QuestionDelegee(BaseModel):
    deleger_a: str
    question: str
    status: str


# ---------------------------------------------------------------------------
# Modèle principal
# ---------------------------------------------------------------------------

class HypothesesOutput(BaseModel):
    session_id: str
    timestamp: str
    description_projet: str
    bloc1_ventes: Bloc1Ventes
    bloc2_achats: Bloc2Achats
    bloc3_charges: Bloc3Charges
    bloc4_encaissements: Bloc4Encaissements
    validation: ResultatValidation
    scenarios: TroisScenarios
    questions_delegees: List[QuestionDelegee] = []
    statut_global: str
    message_final: str
