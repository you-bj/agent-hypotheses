"""
API FastAPI de l'Agent Hypothèses.
Point d'entrée principal exposant les endpoints pour :
- Vérifier l'état du service
- Lancer le dialogue de collecte des hypothèses
- Valider des hypothèses existantes
- Consulter la liste des questions
"""

import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.groq_client import init_groq
from agent.dialogue import conduire_dialogue
from agent.validation import valider_toutes_hypotheses
from agent.output_builder import construire_json_final
from agent.questions import QUESTIONS
from rag.vectorstore import init_chromadb
from rag.embedder import get_embedder


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

load_dotenv()

app = FastAPI(
    title="Agent Hypothèses",
    description=(
        "Agent IA qui collecte les 22 hypothèses financières "
        "d'un entrepreneur marocain pour générer son Business Plan."
    ),
    version="1.0",
)

# --- Initialisation globale des composants ---
try:
    print("🔄 Initialisation du client Groq...")
    client_groq = init_groq()

    chroma_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    print(f"🗄️  Initialisation de ChromaDB ({chroma_path})...")
    collection_chroma = init_chromadb(chroma_path)

    print("🧠 Chargement du modèle d'embeddings...")
    embedder = get_embedder()

    print("✅ Agent Hypothèses prêt")
except Exception as e:
    print(f"❌ Erreur d'initialisation : {e}")
    client_groq = None
    collection_chroma = None
    embedder = None


# ---------------------------------------------------------------------------
# Modèles de requête
# ---------------------------------------------------------------------------

class DemandeHypotheses(BaseModel):
    description_projet: str
    langue: str = "fr"
    session_id: str = ""


class ReponseHypothese(BaseModel):
    session_id: str
    question_id: str
    question_text: str
    reponse: str


class DemandeValidation(BaseModel):
    hypotheses: dict
    description_projet: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    """Vérifie l'état du service et de ses composants."""
    try:
        nb_documents = 0
        if collection_chroma:
            nb_documents = collection_chroma.count()

        return {
            "status": "ok",
            "agent": "Agent Hypothèses",
            "modele": "llama-3.3-70b-versatile",
            "langue": "français",
            "version": "1.0",
            "rag_documents": nb_documents,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ Erreur /health : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/hypotheses/start")
def start_dialogue(demande: DemandeHypotheses):
    """
    Lance le dialogue complet de collecte des 22 hypothèses.

    Reçoit la description du projet et retourne le JSON final
    contenant hypothèses, validation et scénarios.
    """
    try:
        if not client_groq or not collection_chroma or not embedder:
            raise HTTPException(
                status_code=503,
                detail="Service non initialisé. Vérifiez la configuration.",
            )

        session_id = demande.session_id or str(uuid.uuid4())[:8]
        print(f"\n🚀 Nouvelle session : {session_id}")
        print(f"📋 Projet : {demande.description_projet}")

        resultat = conduire_dialogue(
            client_groq=client_groq,
            collection_chroma=collection_chroma,
            embedder=embedder,
            description_projet=demande.description_projet,
        )

        return {
            "session_id": session_id,
            "status": "completed",
            "json_final": resultat.get("json_final"),
            "nb_hypotheses": len(resultat.get("hypotheses", {})),
            "nb_questions_delegees": len(resultat.get("questions_delegees", [])),
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur /hypotheses/start : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/hypotheses/validate")
def validate_hypotheses(demande: DemandeValidation):
    """
    Valide des hypothèses déjà collectées et génère le JSON final
    sans relancer le dialogue interactif.
    """
    try:
        # Validation
        resultat_validation = valider_toutes_hypotheses(demande.hypotheses)

        # Construction du JSON final
        json_final = construire_json_final(
            hypotheses_collectees=demande.hypotheses,
            validation_globale=resultat_validation,
            description_projet=demande.description_projet,
            questions_delegees=[],
        )

        return {
            "status": "validated",
            "json_final": json_final.model_dump(),
            "validation_globale": resultat_validation.get("validation_globale"),
            "nb_alertes": resultat_validation.get("nb_alertes", 0),
            "nb_erreurs": resultat_validation.get("nb_erreurs", 0),
        }

    except Exception as e:
        print(f"❌ Erreur /hypotheses/validate : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/hypotheses/questions")
def get_questions():
    """
    Retourne la liste complète des 22 questions organisées
    en 4 blocs.
    """
    try:
        total = sum(len(questions) for questions in QUESTIONS.values())

        return {
            "total": total,
            "blocs": QUESTIONS,
        }

    except Exception as e:
        print(f"❌ Erreur /hypotheses/questions : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenarios/{session_id}")
def get_scenarios(session_id: str):
    """
    Récupère les scénarios d'une session donnée.
    Disponible après intégration PostgreSQL.
    """
    try:
        return {
            "message": "Endpoint disponible après intégration PostgreSQL",
            "session_id": session_id,
        }

    except Exception as e:
        print(f"❌ Erreur /scenarios : {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Lancement
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
