
# 🚀 Churn Sentinel Plan de Projet 

## 📋 Vue d'Ensemble du Projet

**Nom du projet :** `churn-sentinel`

**Objectif :** Construire un système de prédiction du churn client qui ne se contente pas d'être précis, mais qui est **fiable, observable et capable de s'auto-maintenir**. Le système détecte les changements dans les données, ré-entraîne un nouveau modèle (challenger), et ne le promeut en production que s'il prouve sa supériorité sur le modèle en place (champion).

**Niveau de Maturité Visé :** **Niveau 3 (Automatisation du déploiement)** du modèle de maturité MLOps, avec une implémentation partielle du Niveau 4 (ré-entraînement déclenché par les signaux de production).

**Périmètre :**
- **Socle obligatoire :** Pipeline de données → Modèle → API → Docker → CI/CD → Monitoring.
- **Extension conditionnelle :** Gate Champion/Challenger avec alias MLflow et rollback atomique.

---

## 1. 🏗️ Architecture Cible et Philosophie

La plupart des échecs MLOps ne viennent pas des modèles, mais de **lacunes architecturales** : absence de séparation des environnements, changements silencieux, et manque de traçabilité. L'architecture doit donc séparer explicitement deux boucles :

- **Boucle Interne (Inner Loop)** : L'espace d'expérimentation (notebooks, feature engineering, entraînement). C'est là que le modèle est construit.
- **Boucle Externe (Outer Loop)** : L'espace de production (API, monitoring, ré-entraînement, gate). C'est là que le modèle vit et est maintenu.

**Le pont entre les deux est le Registre de Modèles (MLflow Registry)** , qui stocke non seulement le modèle, mais aussi ses métadonnées (hash du dataset via DVC, commit Git, hyperparamètres), rendant le rollback possible en minutes.

**Flux de Données :**
`Données Brutes → Validation (Pandera) → Préparation → Entraînement (MLflow Tracking) → Registre (@champion) → API (FastAPI) → Monitoring (Evidently) → Ré-entraînement (GitHub Actions) → Gate (Champion/Challenger) → Mise à Jour du Registre`

**Solution :** Avant de coder, produire un diagramme d'architecture (Mermaid ou ASCII) qui matérialise ce flux. Un `Makefile` avec des cibles (`make validate`, `make train`, `make serve`, `make test`) doit permettre d'exécuter chaque étape sans connaître les chemins exacts.

---

## 2. 📊 Données et Stratégie de Modélisation

### Dataset Principal : Telco Customer Churn
- **Source :** Kaggle, OpenML (ID 46280), Hugging Face. Utilisé par les pipelines de référence `Western-1/churn-pipeline` et `aakash1552005/telco-churn-mlops`.
- **Taille :** 7 043 lignes, 21 colonnes.
- **Déséquilibre :** ~73 % non-churners / ~27 % churners.
- **Particularité Critique :** `TotalCharges` est une colonne texte avec 11 valeurs vides. Ces lignes correspondent à des clients avec `tenure = 0` (nouveaux inscrits). **Ne pas les supprimer** ; les imputer par `0` (ou une valeur cohérente). Les supprimer fausserait l'analyse.

### Stratégie Face au Déséquilibre
Pour un projet de 4 mois, **`class_weight='balanced'`** dans les modèles (Scikit-learn/XGBoost) est le choix le plus **sûr et reproductible**. Il évite les risques de fuite de données liés aux techniques de sur-échantillonnage synthétique (SMOTE, ADASYN).

**Option (si le temps le permet) :** Tester **ADASYN + Tomek Links** dans une branche séparée, en appliquant le ré-échantillonnage **uniquement sur le jeu d'entraînement**, jamais sur le jeu de test. Comparer les F1-scores et documenter le choix.

### Validation des Données (Le Chaînon Manquant)
Une validation de schéma en amont est **critique** : si le CSV change de format, le pipeline produit un modèle silencieusement faux. **Pandera** est recommandé pour un projet Python-native (plus léger que Great Expectations).

---

## 3. 🛠️ Stack Technique et Outils Open Source

| Outil | Rôle | Justification Critique |
| :--- | :--- | :--- |
| **MLflow** | Suivi d'expériences, Registre de Modèles, **Alias** (`@champion`, `@challenger`) | Standard de l'industrie. Les **alias** permettent une promotion et un rollback **atomiques** en un seul appel API. |
| **DVC** | Versioning des données | Permet de répondre à "quel dataset a entraîné quel modèle ?" via un hash MD5. Essentiel pour la reproductibilité. |
| **FastAPI** | API de serving (`/predict`) | Léger, rapide, avec validation Pydantic intégrée. **Sérialiser le préprocesseur** (joblib) et le charger dans l'API. |
| **Docker + Compose** | Conteneurisation | Isole l'API et ses dépendances. Indispensable pour un déploiement reproductible. |
| **Evidently AI** | Détection de dérive | Génère des rapports HTML. **Configurer explicitement les seuils** : `PSI=0.2` pour les numériques, `chi2=0.3` pour les catégorielles. |
| **Pandera** | Validation des données | **Shift-left** : bloque le pipeline si le schéma des données est corrompu. |
| **GitHub Actions** | CI/CD et Ré-entraînement | Workflow à **trois déclencheurs** (`schedule`, `workflow_dispatch`, `repository_dispatch`). **`concurrency: group: retrain-${{ github.repository }}`** avec **`cancel-in-progress: false`**. |
| **Pytest** | Tests | Tests unitaires, tests d'intégration, **test de skew** (comparer les features d'entraînement et de serving). |
| **Gradio / Streamlit** | Dashboard | Déploiement gratuit sur **Hugging Face Spaces** pour une démo interactive. |

---

## 4. 🎯 Objectifs Détaillés et Critères de Réussite

### Objectif 1 — Pipeline de Données Fiable
- **Quoi :** Valider, versionner et préparer les données de manière reproductible.
- **Comment :** Pandera pour la validation, DVC pour le versioning, `prepare.py` pour le préprocessing.
- **Critère de Réussite :** Le pipeline échoue proprement si le schéma des données est invalide. Le dataset est versionné avec DVC.

### Objectif 2 — Modélisation et Suivi d'Expériences
- **Quoi :** Entraîner plusieurs modèles et suivre chaque expérience.
- **Comment :** Comparer LogisticRegression, RandomForest, XGBoost avec MLflow Tracking. Utiliser **F1-score et PR-AUC** comme métriques principales.
- **Critère de Réussite :** Un run MLflow clair avec les métriques des 3 modèles. Le meilleur modèle est enregistré dans le Registre avec l'alias `@champion`.

### Objectif 3 — API de Serving Robuste
- **Quoi :** Exposer le modèle via une API sécurisée et conteneurisée.
- **Comment :** FastAPI avec endpoint `/predict`, validation Pydantic, **API Key** (`X-API-Key`) et **rate limiting**. Sérialiser le préprocesseur (`joblib`) et le charger dans l'API.
- **Critère de Réussite :** L'API répond en local et dans Docker. Un `curl` avec la clé API renvoie une prédiction. Un `curl` sans clé est rejeté (403).

### Objectif 4 — Monitoring et Détection de Dérive
- **Quoi :** Surveiller la qualité du modèle et détecter les changements de distribution.
- **Comment :** Evidently AI avec des seuils **explicitement configurés** (`PSI=0.2` numérique, `chi2=0.3` catégorielle). Générer un rapport HTML.
- **Critère de Réussite :** Un rapport Evidently montre une dérive sur un jeu de simulation. Les seuils sont documentés.

### Objectif 5 — Ré-entraînement Contrôlé et Gate Champion/Challenger
- **Quoi :** Automatiser le ré-entraînement sans jamais dégrader la production.
- **Comment :** Workflow GitHub Actions avec trois déclencheurs et `cancel-in-progress: false`. `retrain.py` entraîne un challenger avec un **replay buffer** (100–200 échantillons anciens). `gate.py` compare champion et challenger sur un jeu de validation commun et ne promeut que si le challenger est **significativement meilleur**.
- **Critère de Réussite :** Le gate fonctionne : un challenger moins bon est **rejeté**, un challenger meilleur est **promu** (alias `@champion` déplacé atomiquement). Le **rollback** est testé et documenté.

### Objectif 6 — Démonstration et Documentation
- **Quoi :** Un dashboard interactif, un rapport et une soutenance.
- **Comment :** Dashboard Gradio sur Hugging Face Spaces. Rapport structuré. **Runbook** d'incident (`docs/runbook.md`).
- **Critère de Réussite :** Le dashboard est accessible. Le runbook est rédigé. La soutenance est répétée.

---

## 5. 📅 Plan d'Action Détaillé (Mois par Mois, Semaine par Semaine)

### Mois 1 — Le Socle : Données, Modèle et Suivi d'Expériences

#### Semaine 1 — Structure, Validation des Données et EDA

**Tâches :**
1.  **Créer la structure du dépôt** : `data/`, `src/`, `tests/`, `.github/workflows/`, `Dockerfile`, `docker-compose.yml`, `Makefile`, `requirements.txt`, `README.md`.
2.  **Créer `src/data/validate.py` avec Pandera** : définir un `DataFrameModel` avec les colonnes attendues, les types, et les contraintes (par exemple, `TotalCharges` nullable uniquement si `tenure == 0`).
3.  **Versionner les données avec DVC** : `dvc init`, `dvc add data/raw/telco_churn.csv`, `git add .`, `git commit`.
4.  **Lancer l'EDA** : distribution de la cible, valeurs manquantes (`TotalCharges`), types de features.

**Critère de « fini » :** Le schéma Pandera valide le CSV. Le dataset est versionné avec DVC. Le notebook d'EDA est commité.

---

#### Semaine 2 — Préparation des Données et Entraînement avec MLflow

**Tâches :**
1.  **Créer `src/data/prepare.py`** : charger le CSV, corriger `TotalCharges`, encoder les catégorielles, normaliser les numériques, **sérialiser le préprocesseur** avec `joblib` dans `models/preprocessor.joblib`.
2.  **Créer `src/models/train.py`** : entraîner 2–3 modèles (LogisticRegression, RandomForest, XGBoost) avec `class_weight='balanced'`, tracker chaque run dans MLflow (paramètres, métriques F1/PR-AUC, modèle).
3.  **Lancer l'entraînement** : `python src/models/train.py`.
4.  **Vérifier MLflow UI** (`mlflow ui`) : comparer les runs.

**Critère de « fini » :** Trois runs MLflow visibles avec F1 et ROC-AUC. Le préprocesseur est sérialisé.

---

#### Semaine 3 — Enregistrement du Modèle et Alias `@champion`

**Tâches :**
1.  **Sélectionner le meilleur modèle** (F1 le plus élevé).
2.  **Enregistrer le modèle dans le Registre avec l'alias `@champion`** : utiliser `mlflow.register_model` puis `client.set_registered_model_alias`.
3.  **Écrire les tests unitaires** : vérifier que le modèle se charge depuis l'alias `@champion`.

**Critère de « fini » :** L'alias `@champion` pointe vers la bonne version. Les tests passent.

---

#### Semaine 4 — API FastAPI Locale avec Sécurité

**Tâches :**
1.  **Créer `src/api/security.py`** : implémenter `verify_api_key` (lit `X-API-Key` depuis les variables d'environnement) et un rate limiter (`slowapi`, 100/minute).
2.  **Créer `src/api/main.py`** : endpoint `/predict` qui charge le modèle via `models:/churn_classifier@champion`, charge le préprocesseur (`joblib`), applique la transformation, et renvoie la probabilité de churn.
3.  **Tester avec `curl`** : avec et sans clé API.

**Critère de « fini » :** L'API répond avec une prédiction. Sans clé API, elle renvoie 403.

---

### Mois 2 — Mise en Production et Monitoring

#### Semaine 5 — Dockerisation de l'API

**Tâches :**
1.  **Écrire le `Dockerfile`** multi-stage : `python:3.11-slim`, copier `requirements.txt`, installer les dépendances, copier `src/` et `models/`, exposer le port 8000.
2.  **Écrire `docker-compose.yml`** : services `api` et `mlflow`.
3.  **Lancer** : `docker-compose up --build`.
4.  **Vérifier** : `curl http://localhost:8000/health`.

**Critère de « fini » :** L'API tourne dans Docker.

---

#### Semaine 6 — Monitoring avec Evidently AI

**Tâches :**
1.  **Créer `src/monitoring/drift_report.py`** : utiliser `DataDriftPreset` avec `cat_method="psi"`, `cat_threshold="0.3"`, `num_method="psi"`, `num_threshold="0.2"`.
2.  **Créer un jeu de « production » simulé** : filtrer les contrats `Two year` pour créer un changement de distribution.
3.  **Générer le rapport HTML** et vérifier qu'une dérive est détectée.

**Critère de « fini » :** Rapport Evidently généré. Seuils documentés.

---

#### Semaine 7 — Test de Skew et Validation CI

**Tâches :**
1.  **Créer `tests/test_skew.py`** : prendre 1 000 échantillons identiques, les passer dans le pipeline d'entraînement et dans le pipeline de serving (via `TestClient`), et vérifier que les vecteurs de features sont identiques à la tolérance près.
2.  **Ajouter Pandera à la CI** : test `test_data_schema` qui valide le CSV.
3.  **Configurer `.github/workflows/ci.yml`** (première version) pour exécuter pytest.

**Critère de « fini » :** Les tests de skew et de schéma passent en local.

---

#### Semaine 8 — Documentation des Seuils et Premier Test de Charge (Optionnel)

**Tâches :**
1.  **Documenter dans le README** : `PSI > 0.2` (numérique) → dérive significative ; `PSI ≥ 0.3` (catégorielle) → dérive significative ; taille minimale de batch : 200 échantillons.
2.  **(Optionnel) Test de charge avec Locust ou k6** : définir un SLO (p95 < 200 ms) et vérifier que l'API le respecte.

**Critère de « fini » :** README complet.

---

### Mois 3 — Automatisation et Gate

#### Semaine 9 — CI/CD de Base

**Tâches :**
1.  **Créer `.github/workflows/ci.yml`** : lint, tests, build Docker.
2.  **Pousser et vérifier que la CI passe.**

**Critère de « fini » :** CI verte sur `main`.

---

#### Semaine 10 — Workflow de Ré-entraînement avec Trois Déclencheurs

**Tâches :**
1.  **Créer `.github/workflows/retrain.yml`** : trois déclencheurs (`schedule`, `workflow_dispatch`, `repository_dispatch`), `concurrency: group: retrain-${{ github.repository }}`, `cancel-in-progress: false`.
2.  **Créer `src/models/retrain.py`** : charger les données avec DVC, **replay buffer** (mélanger 100–200 échantillons du jeu d'origine), entraîner un challenger, l'enregistrer avec l'alias `@challenger`.

**Critère de « fini » :** Le workflow produit un `@challenger`.

---

#### Semaine 11 — Gate Champion/Challenger

**Tâches :**
1.  **Créer `src/models/gate.py`** : charger `@champion` et `@challenger`, évaluer les deux sur un jeu de validation commun, comparer les métriques (par exemple, F1 Gain ≥ +0.01), et si le challenger est meilleur, déplacer l'alias `@champion` via `set_registered_model_alias`.
2.  **Tester le rejet** : créer un challenger volontairement mauvais et vérifier qu'il n'est **pas** promu.
3.  **Tester le rollback** : simuler une promotion, puis un problème, et vérifier que `set_registered_model_alias` ramène `@champion` à la version précédente.

**Critère de « fini » :** Le gate fonctionne. Le rollback est testé.

---

#### Semaine 12 — Dashboard Gradio sur HF Spaces

**Tâches :**
1.  **Créer `app.py`** avec Gradio : formulaire pour saisir les features, appel à l'API `/predict`, affichage de la probabilité de churn.
2.  **Déployer sur Hugging Face Spaces.**

**Critère de « fini » :** Dashboard accessible. Démo de 2 minutes répétée.

---

### Mois 4 — Finalisation et Soutenance

#### Semaine 13 — Audit Trail et Runbook

**Tâches :**
1.  **Créer `reports/promotion_audit.jsonl`** : logger chaque décision de promotion (timestamp, version challenger, métriques, hash DVC, commit Git).
2.  **Rédiger `docs/runbook.md`** : que faire si le gate rejette un challenger, si l'API tombe (rollback via `set_registered_model_alias`), si Evidently détecte une dérive critique.
3.  **Rédiger un postmortem simulé**.

**Critère de « fini » :** Audit trail généré. Runbook rédigé.

---

#### Semaine 14 — Polissage et Répétition

**Tâches :**
1.  **Relecture du code et des tests.**
2.  **Répétition de la démo live** (2 fois) : prédiction via le dashboard, rapport de dérive Evidently, déclenchement manuel du ré-entraînement (`workflow_dispatch`), gate qui rejette un mauvais challenger, rollback en un appel.

**Critère de « fini » :** Soutenance répétée et chronométrée.

---

#### Semaine 15 — Soutenance

---

## 6. ⚠️ Risques Critiques et Solutions

| Risque | Solution |
| :--- | :--- |
| **Échec Silencieux** | Evidently dès le Mois 2 avec une **baseline solide**. |
| **Train-Serve Skew** | Sérialiser le préprocesseur (`joblib`) + test de skew dans la CI. |
| **Fatigue d'Alertes** | Machine à états (3 fenêtres consécutives) + taille de batch > 200. |
| **Oubli Catastrophique** | Replay buffer (100–200 échantillons). |
| **Promotion Dangereuse** | Gate avec seuils explicites + verrouillage du schéma Pydantic. |
| **Concurrence CI** | `concurrency: group: retrain-${{ github.repository }}`, `cancel-in-progress: false`. |
| **Épuisement du Crédit Azure** | Azure Container Apps avec scale-to-zero. Alertes de budget. |
| **API Ouverte** | API Key (`X-API-Key`) + rate limiting (`slowapi`). |
