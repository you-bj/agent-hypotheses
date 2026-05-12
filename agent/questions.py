"""
Module contenant les 22 hypothèses organisées en 4 blocs.
Chaque hypothèse est un dictionnaire avec les champs :
id, question, variable, type.
"""

QUESTIONS = {
    "bloc1_ventes": [
        {
            "id": "H1",
            "question": "Quel est votre segment client principal ? (B2C, B2B ou Mixte)",
            "variable": "segment_client",
            "type": "choix"
        },
        {
            "id": "H2",
            "question": "Quel est votre prix de vente unitaire en MAD ?",
            "variable": "prix_vente_unitaire",
            "type": "numerique"
        },
        {
            "id": "H3",
            "question": "Proposez-vous un abonnement mensuel ? Si oui, quel est le montant en MAD ?",
            "variable": "abonnement_mensuel",
            "type": "numerique"
        },
        {
            "id": "H4",
            "question": "Combien de clients prévoyez-vous le premier mois ?",
            "variable": "nb_clients_mois1",
            "type": "numerique"
        },
        {
            "id": "H5",
            "question": "Quel est votre taux de croissance mensuel estimé (en %) ?",
            "variable": "taux_croissance_mensuel",
            "type": "pourcentage"
        },
        {
            "id": "H6",
            "question": "Quel est votre taux de fidélisation client estimé (en %) ?",
            "variable": "taux_fidelisation",
            "type": "pourcentage"
        },
        {
            "id": "H7",
            "question": "Votre activité est-elle saisonnière ? Si oui, quels sont les mois forts et les mois faibles ?",
            "variable": "saisonnalite",
            "type": "booleen_details"
        },
    ],

    "bloc2_achats": [
        {
            "id": "H8",
            "question": "Quel est le type de votre activité ? (Service, Produit ou Hybride)",
            "variable": "type_activite",
            "type": "choix"
        },
        {
            "id": "H9",
            "question": "Quel est le coût de fabrication ou de revient unitaire en MAD ?",
            "variable": "cout_fabrication_unitaire",
            "type": "numerique"
        },
        {
            "id": "H10",
            "question": "Quelle est la quantité minimum de commande auprès de vos fournisseurs ?",
            "variable": "quantite_min_commande",
            "type": "numerique"
        },
        {
            "id": "H11",
            "question": "Quel est le coût de votre infrastructure numérique par mois en MAD ? (hébergement, serveurs, SaaS...)",
            "variable": "cout_infra_numerique",
            "type": "numerique"
        },
        {
            "id": "H12",
            "question": "Quel est le délai moyen de livraison de vos fournisseurs en jours ?",
            "variable": "delai_fournisseur_jours",
            "type": "numerique"
        },
    ],

    "bloc3_charges": [
        {
            "id": "H13",
            "question": "Quel est le montant de votre loyer mensuel en MAD ?",
            "variable": "loyer_mensuel",
            "type": "numerique"
        },
        {
            "id": "H14",
            "question": "Quels sont les salaires mensuels de votre équipe ? (détaillez par poste si possible)",
            "variable": "salaires_equipe",
            "type": "numerique_details"
        },
        {
            "id": "H15",
            "question": "Quel est le montant mensuel de vos charges d'utilités en MAD ? (eau, électricité, internet...)",
            "variable": "charges_utilites",
            "type": "numerique"
        },
        {
            "id": "H16",
            "question": "Quel est le coût mensuel de vos licences logicielles en MAD ?",
            "variable": "licences_logicielles",
            "type": "numerique"
        },
        {
            "id": "H17",
            "question": "Quel est votre budget marketing mensuel en MAD ?",
            "variable": "budget_marketing",
            "type": "numerique"
        },
        {
            "id": "H18",
            "question": "Quel est le montant annuel de vos honoraires de conseil en MAD ?",
            "variable": "honoraires_conseil",
            "type": "numerique"
        },
        {
            "id": "H19",
            "question": "Quel est le montant total de vos investissements initiaux en MAD ?",
            "variable": "investissements_initiaux",
            "type": "numerique"
        },
        {
            "id": "H20",
            "question": "Quel est le coût de vos certifications et normes en MAD ?",
            "variable": "certifications",
            "type": "numerique"
        },
        {
            "id": "H21",
            "question": "Avez-vous des emprunts ? Si oui, quel est le montant, le taux d'intérêt et la durée ?",
            "variable": "emprunts",
            "type": "numerique_details"
        },
    ],

    "bloc4_encaissements": [
        {
            "id": "H22",
            "question": "Quelle est la nature de vos clients pour les encaissements ? (B2C, B2B ou Mixte)",
            "variable": "nature_clients_encaissements",
            "type": "choix"
        },
    ],
}
