# Agent Hypothèses - Module Pédagogique Intelligent

Plateforme IA End-to-End pour l'accompagnement à la création d'entreprise au Maroc.

## 🎯 Objectif

L'Agent Hypothèses est un module IA qui collecte les 22 hypothèses financières d'un entrepreneur marocain à travers un dialogue conversationnel intelligent, les valide selon la méthode Chauvin, et génère automatiquement 3 scénarios financiers (pessimiste, réaliste, optimiste).

## 🏗️ Architecture

### Workflow Multi-Agents
```
Angular → FastAPI → SLM Phi-3 Mini (classification intention) 
→ Agent Contrôleur n8n → POST /hypotheses/start 
→ Dialogue 22 questions (RAG Chauvin + Groq) 
→ Validation Chauvin → JSON HypothesesOutput 
→ Agent Finance (POST /plan) → Agent Business Plan → PDF final
```

### Stack Technique
- **Langage** : Python 3.10.11
- **API REST** : FastAPI + uvicorn (port 8000)
- **LLM** : Groq API (llama-3.3-70b-versatile)
- **RAG** : LangChain + ChromaDB (280 documents)
- **Embeddings** : sentence-transformers (all-MiniLM-L6-v2)
- **Validation** : Pydantic (schéma HypothesesOutput)
- **Orchestration** : n8n

## 📁 Structure du Projet

```
agent_hypotheses/
├── .env                    # Variables d'environnement
├── main.py                 # API FastAPI principale
├── requirements.txt        # Dépendances Python
├── agent/                  # Logique métier
│   ├── dialogue.py        # Cœur conversationnel
│   ├── groq_client.py     # Connexion LLM
│   ├── validation.py      # Règles de Chauvin
│   ├── questions.py       # 22 questions structurées
│   ├── scenarios.py       # 3 projections financières
│   └── output_builder.py  # Construction JSON final
├── rag/                    # Pipeline RAG
│   ├── vectorstore.py      # ChromaDB
│   ├── embedder.py         # Modèle d'embeddings
│   └── retriever.py        # Recherche sémantique
├── schemas/                # Schémas Pydantic
│   └── output_schema.py    # Contrat JSON
├── data/                   # Données de référence
│   └── scenarios_reference.json
├── scripts/                # Tests et validation
│   ├── test_dialogue.py
│   ├── test_validation.py
│   ├── test_json_final.py
│   └── test_scenarios_rag.py
└── venv/                   # Environnement virtuel
```

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.10+
- API Key Groq (gratuite)

### 1. Cloner le projet
```bash
git clone <repository-url>
cd agent_hypotheses
```

### 2. Créer l'environnement virtuel
```bash
py -3.10 -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer l'environnement
Créer un fichier `.env` avec :
```env
GROQ_API_KEY=votre_cle_groq
CHROMA_DB_PATH=./data/chroma_db
POSTGRES_URL=  # Optionnel
```

### 5. Lancer le serveur
```bash
python main.py
```

Le serveur démarre sur `http://localhost:8000`

## 📚 Comment Utiliser l'Agent

### ⚠️ Important : L'agent est une API REST, pas un programme terminal

Quand vous lancez `python main.py`, l'agent ne pose pas les questions directement dans le terminal. Il démarre un **serveur web API** sur `http://localhost:8000`.

### 🚀 Étapes pour utiliser l'agent

#### 1. Démarrer le serveur
```bash
python main.py
# Output attendu :
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Started server process
```

#### 2. Accéder à l'interface API
Ouvrez votre navigateur et allez sur :
```
http://localhost:8000/docs
```

#### 3. Lancer le dialogue d'hypothèses
1. Cherchez l'endpoint **POST /hypotheses/start**
2. Cliquez sur **"Try it out"**
3. Cliquez sur **"Execute"** (sans paramètres)
4. L'agent commence le dialogue avec la première question

#### 4. Répondre aux 22 questions
L'agent va vous poser les questions une par une :
- **Bloc 1** (H1-H7) : Ventes, clients, prix, croissance
- **Bloc 2** (H8-H12) : Type activité, fabrication, fournisseurs  
- **Bloc 3** (H13-H21) : Charges fixes, loyer, salaires, marketing
- **Bloc 4** (H22) : Nature clients, délais encaissement

#### 5. Obtenir les résultats
À la fin des 22 questions, l'agent génère automatiquement :
- ✅ **JSON structuré** avec toutes les hypothèses
- ✅ **Validation Chauvin** (3 règles financières)
- ✅ **3 scénarios** (pessimiste, réaliste, optimiste)
- ✅ **Messages pédagogiques** si alertes

### 📋 Documentation API

#### Endpoints disponibles

| Méthode | Endpoint | Description | Statut |
|---------|----------|-------------|--------|
| GET | `/health` | État du service + nb docs RAG | ✅ 200 OK |
| POST | `/hypotheses/start` | Lance le dialogue complet | ✅ 200 OK |
| POST | `/hypotheses/validate` | Valide sans dialogue | ✅ 200 OK |
| GET | `/hypotheses/questions` | Liste des 22 questions | ✅ 200 OK |
| GET | `/scenarios/{id}` | Historique de session | ⏳ En attente |

#### Documentation interactive
Accédez à `http://localhost:8000/docs` pour la documentation Swagger interactive.

### 🎯 Pour les évaluateurs : Démonstration rapide

Pour tester rapidement l'agent :

1. **Démarrer** : `python main.py`
2. **Navigateur** : `http://localhost:8000/docs`
3. **Tester** : POST /hypotheses/start → Execute
4. **Observer** : Le dialogue commence avec la première question sur les ventes
5. **Répondre** : Donnez des réponses simples (ex: "épicerie", "30 clients", "150 MAD")
6. **Vérifier** : À la fin, vous obtenez le JSON complet avec 3 scénarios

### 🔧 Points techniques importants

- **RAG intégré** : Chaque question est enrichie avec le livre Chauvin (280 documents)
- **Validation en temps réel** : Les règles Chauvin s'appliquent pendant le dialogue
- **Guardrails** : L'agent détecte si vous posez des questions ou répondez hors sujet
- **JSON final** : Structure prête pour l'Agent Finance de la plateforme

## 🧠 Fonctionnalités Clés

### 1. Collecte des 22 Hypothèses
Organisées en 4 blocs selon la méthode Chauvin :
- **Bloc 1** : Ventes, clients, prix, croissance (H1-H7)
- **Bloc 2** : Type activité, fabrication, fournisseurs (H8-H12)
- **Bloc 3** : Charges fixes, loyer, salaires, marketing (H13-H21)
- **Bloc 4** : Nature clients, délais encaissement (H22)

### 2. Validation Chauvin
3 règles de validation automatiques :
- **Règle 1** : Seuil de rentabilité
- **Règle 2** : Symétrie du financement
- **Règle 3** : Cohérence prix/coût fabrication

### 3. Génération de Scénarios
3 projections automatiques :
- **Pessimiste** : ×0.7 (30% moins de clients)
- **Réaliste** : ×1.0 (hypothèses saisies)
- **Optimiste** : ×1.3 (30% plus de clients)

### 4. RAG Intégration
- **280 documents** indexés (270 chunks livre Chauvin + 10 scénarios marocains)
- **Recherche sémantique** avec similarité cosinus
- **Enrichissement** des prompts avec contexte pertinent

## 📊 Métriques de Performance

| Indicateur | Valeur obtenue | Statut |
|------------|----------------|--------|
| Connexion Groq | 1 070 ms | ✅ < 2s |
| Documents RAG | 280 indexés | ✅ |
| Questions couvertes | 22 / 22 | ✅ |
| Endpoints API | 5 / 5 | ✅ |
| Scénarios générés | 3 automatiques | ✅ |
| JSON final | 12 champs validés | ✅ |

## 🧪 Tests

### Exécuter les tests de validation
```bash
# Test dialogue complet
python scripts/test_dialogue.py

# Test validation règles Chauvin
python scripts/test_validation.py

# Test construction JSON final
python scripts/test_json_final.py

# Test recherche RAG
python scripts/test_scenarios_rag.py
```

## 💡 Exemple d'Utilisation

### Requête API
```json
POST /hypotheses/start
{
  "description_projet": "Épicerie de quartier à Tanger",
  "langue": "fr"
}
```

### Réponse
```json
{
  "session_id": "cd342c82",
  "status": "completed",
  "json_final": {
    "bloc1_ventes": {...},
    "bloc2_achats": {...},
    "bloc3_charges": {...},
    "bloc4_encaissements": {...},
    "validation_globale": {...},
    "trois_scenarios": {...}
  },
  "nb_hypotheses": 22,
  "nb_questions_delegees": 0
}
```

## 🔧 Configuration

### Variables d'environnement
- `GROQ_API_KEY` : Clé API Groq (obligatoire)
- `CHROMA_DB_PATH` : Chemin base vectorielle (défaut: `./data/chroma_db`)
- `POSTGRES_URL` : Connexion PostgreSQL (optionnel)

### Paramètres modifiables
- Température LLM : 0.3 (équilibre créativité/précision)
- Nombre de documents RAG : 3 (par requête)
- Tentatives max par question : 3
- Seuil validation Chauvin : configurable dans `validation.py`

## 🚧 Prochaines Étapes

- [ ] Connexion PostgreSQL pour sessions persistantes
- [ ] Extension Darija et Arabe
- [ ] Intégration workflow n8n complet
- [ ] Golden Set 50 scénarios de test
- [ ] Tests avec profils entrepreneurs réels
- [ ] Module OCR formulaires

## 📈 Résultats Attendus

### Scénario Épicerie Tanger (exemple)
| Indicateur | Pessimiste | Réaliste | Optimiste |
|------------|------------|----------|-----------|
| Clients mois 1 | 21 | 30 | 39 |
| CA mois 1 | 3 150 MAD | 4 500 MAD | 5 850 MAD |
| CA annuel | 67 360 MAD | 96 229 MAD | 125 098 MAD |
| Mois rentabilité | Mois 22 | Mois 19 | Mois 16 |

## 🤝 Contribution

Ce projet est développé dans le cadre d'un Projet de Fin d'Études (Licence Data Analytics, FSTT).

### Auteur
- **Étudiant** : [Votre Nom]
- **Formation** : Licence Data Analytics
- **Établissement** : Université Abdelmalek Essaâdi - FSTT
- **Année** : 2025-2026

### Licence
Ce projet est sous licence académique.

## 📞 Support

Pour toute question ou problème :
1. Consulter la documentation API (`/docs`)
2. Vérifier les logs du serveur
3. Exécuter les scripts de test dans `/scripts`

---

**Agent Hypothèses** - Module Pédagogique Intelligent pour l'Entrepreneuriat Marocain 🇲🇦
