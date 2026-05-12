# 🚀 Guide Click-by-Click : Pusher le Projet sur GitHub

## 📋 Prérequis
- Compte GitHub créé
- Git installé sur votre machine
- Projet Agent Hypothèses prêt

---

## 🔧 Étape 1 : Initialiser Git Local
1. **Ouvrir un terminal** dans le dossier du projet :
   ```bash
   cd c:\Users\hp\Desktop\agent_hypotheses
   ```

2. **Initialiser le dépôt Git** :
   ```bash
   git init
   ```

3. **Vérifier le statut** :
   ```bash
   git status
   ```

---

## 🌐 Étape 2 : Créer le Dépôt GitHub
1. **Se connecter à GitHub** : https://github.com

2. **Créer un nouveau dépôt** :
   - Cliquer sur **"+"** en haut à droite
   - Choisir **"New repository"**
   - Nom : `agent-hypotheses`
   - Description : `Agent IA pour collecte hypothèses financières entrepreneurs marocains`
   - **Public** (ou Private si confidentiel)
   - **NE PAS** cocher "Add a README file" (on en a déjà un)
   - Cliquer sur **"Create repository"**

3. **Copier l'URL du dépôt** :
   ```
   https://github.com/VOTRE_USERNAME/agent-hypotheses.git
   ```

---

## 🔗 Étape 3 : Lier Local et Distant
1. **Ajouter le remote** :
   ```bash
   git remote add origin https://github.com/you-bj/agent-hypotheses.git
   ```

2. **Vérifier la connexion** :
   ```bash
   git remote -v
   ```

---

## 📝 Étape 4 : Premier Commit
1. **Ajouter tous les fichiers** :
   ```bash
   git add .
   ```

2. **Vérifier ce qui sera commité** :
   ```bash
   git status
   ```
   *Vérifiez que `.env` n'apparaît PAS grâce au .gitignore*

3. **Faire le premier commit** :
   ```bash
   git commit -m "Initial commit : Agent Hypothèses PFE Data Analytics"
   ```

---

## ⬆️ Étape 5 : Premier Push
1. **Choisir la branche principale** :
   ```bash
   git branch -M main
   ```

2. **Pusher vers GitHub** :
   ```bash
   git push -u origin main
   ```

3. **S'authentifier** si demandé :
   - Entrer votre email GitHub
   - Entrer votre token GitHub (pas votre mot de passe !)

---

## ✅ Étape 6 : Vérification
1. **Rafraîchir la page GitHub** : votre code doit apparaître

2. **Vérifier les fichiers présents** :
   - ✅ README.md
   - ✅ main.py
   - ✅ requirements.txt
   - ✅ .gitignore
   - ✅ Tous les dossiers (agent/, rag/, schemas/, etc.)

3. **Vérifier les fichiers ABSENTS** :
   - ❌ .env (protégé par .gitignore)
   - ❌ venv/ (protégé par .gitignore)
   - ❌ __pycache__/ (protégé par .gitignore)

---

## 🔄 Pour les futurs changements

### Ajouter des modifications
```bash
git add .
git commit -m "Description du changement"
git push
```

### Vérifier le statut
```bash
git status
```

### Voir l'historique
```bash
git log --oneline
```

---

## 🛡️ Sécurité : Fichiers Ignorés (.gitignore)

### Fichiers PROTÉGÉS (non envoyés sur GitHub) :
- `.env` - Contient votre clé API Groq 🔑
- `venv/` - Environnement virtuel Python
- `__pycache__/` - Fichiers cache Python
- `data/chroma_db/` - Base de données vectorielle
- `*.log` - Fichiers de logs
- `*.pdf` - Documents PDF générés

### Fichiers PARTAGÉS (envoyés sur GitHub) :
- `main.py` - Code principal ✅
- `requirements.txt` - Dépendances ✅
- `README.md` - Documentation ✅
- `agent/` - Logique métier ✅
- `rag/` - Pipeline RAG ✅
- `schemas/` - Schémas Pydantic ✅
- `scripts/` - Tests et validation ✅

---

## 🎯 Résultat Final

Votre projet est maintenant sur GitHub : 
**https://github.com/VOTRE_USERNAME/agent-hypotheses**

N'importe qui peut maintenant :
- Cloner votre projet
- Lire le README pour comprendre
- Installer les dépendances
- Lancer le serveur API

---

## ⚠️ Points Importants

1. **Jamais de clé API dans Git** : Le .gitignore protège votre .env
2. **Documentation à jour** : README.md est votre vitrine
3. **Commits clairs** : Messages explicatifs pour chaque changement
4. **Branche main** : Toujours la version stable

---

## 🆘 En cas de problème

### Erreur d'authentification
```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"
```

### Conflit de push
```bash
git pull origin main
git push origin main
```

### Reset complet (dernier recours)
```bash
git reset --hard HEAD~1
```

---

**🎉 Félicitations ! Votre Agent Hypothèses est maintenant sur GitHub !**
