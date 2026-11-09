# 🎯 Churn Sentinel — Le Projet en Bref

## 🚀 C'est quoi ?

Un système de prédiction du churn client qui **se maintient tout seul à jour**. Il ne se contente pas d'être précis : il détecte quand les données changent, ré-entraîne un nouveau modèle, et ne le met en production **que s'il est meilleur** que l'ancien.

**Niveau de maturité visé :** Niveau 3 MLOps (Automatisation du déploiement), avec une implémentation partielle du Niveau 4 (ré-entraînement déclenché par les signaux de production).

**En 3 étapes :**
1. **Entraîner** un modèle sur Telco Customer Churn → prédit qui va partir.
2. **Déployer** une API sécurisée → répond en temps réel.
3. **Surveiller** → si dérive détectée, ré-entraîne et promeut si meilleur.

---

## 🏗️ Architecture

**Deux boucles :**
- **Interne** : EDA, entraînement, comparaison de modèles.
- **Externe** : serving, monitoring, ré-entraînement, gate, rollback.

**Le pont** : le Registre MLflow (modèle + métadonnées : hash DVC, commit Git, hyperparamètres) → rollback en **un seul appel API**.

**Flux :**
`Données → Pandera → Préparation → MLflow → @champion → FastAPI → Evidently → GitHub Actions → Gate → @champion mis à jour`

---

## 🛠️ Stack Technique (Résumé)

| Catégorie | Outils | Rôle clé |
| :--- | :--- | :--- |
| **Données** | DVC + Pandera | Versioning + validation de schéma (shift-left) |
| **Modélisation** | Scikit-learn / XGBoost | `class_weight='balanced'` |
| **Suivi & Registre** | MLflow | Alias `@champion` / `@challenger` (promotion atomique) |
| **Serving** | FastAPI + Pydantic + API Key | API sécurisée + validation |
| **Déploiement** | Docker + Azure Container Apps | Scale-to-zero (protège le crédit 150 $) |
| **Monitoring** | Evidently AI + SkewSentry | Dérive (PSI=0.2 num., chi2=0.3 cat.) + train-serve skew |
| **CI/CD** | GitHub Actions + pytest | 3 déclencheurs + `cancel-in-progress: false` |
| **Démo** | Gradio sur HF Spaces | Dashboard interactif gratuit |

---

## 🎯 Objectifs (Critères de Réussite)

| Objectif | Réussi si... |
| :--- | :--- |
| **Pipeline fiable** | Échoue si Pandera est violé. Dataset versionné DVC. |
| **Modélisation suivie** | 3 runs MLflow comparés. `@champion` enregistré. |
| **API sécurisée** | `/predict` répond avec API Key, 403 sans clé. |
| **Monitoring actif** | Rapport Evidently montre une dérive simulée. |
| **Ré-entraînement contrôlé** | `@challenger` produit avec replay buffer. |
| **Gate opérationnel** | Mauvais challenger rejeté, bon promu, rollback testé. |
| **Démo & doc** | Dashboard HF Spaces + runbook + soutenance répétée. |

---

## 📅 Calendrier (4 Mois)

| Mois | Focus | Livrables Clés |
| :--- | :--- | :--- |
| **M1** | Socle : données, modèle, API locale | Pandera + DVC + 3 runs MLflow + `@champion` + API locale |
| **M2** | Production : Docker, Evidently, skew | API dockerisée + rapport dérive + test skew dans CI |
| **M3** | Automatisation : CI/CD, retrain, gate | CI verte + `retrain.yml` (3 déclencheurs) + gate + dashboard HF |
| **M4** | Finalisation : rollback, audit, soutenance | Rollback testé + runbook + rapport + soutenance |

---

## ⚠️ Risques Clés et Parades

| Risque | Parade |
| :--- | :--- |
| **Échec silencieux** (modèle dégradé, API 200) | Evidently dès M2 avec baseline solide |
| **Train-serve skew** (features différentes) | Préprocesseur sérialisé + test SkewSentry dans CI |
| **Fatigue d'alertes** | 3 fenêtres consécutives + batch > 200 |
| **Oubli catastrophique** | Replay buffer 100–200 échantillons |
| **Promotion dangereuse** | Pydantic verrouille le schéma + gate vérifie la signature |
| **Concurrence CI** | `cancel-in-progress: false` + idempotence (hash DVC) |
| **Crédit Azure épuisé** | Container Apps `min-replicas: 0` + alertes budget |
| **API ouverte** | API Key + rate limiting (100/min) |

---

## 🧪 Test d'Acceptation Final

**Soumettre un modèle délibérément moins bon et prouver que le pipeline refuse de le déployer.** Si tu réussis ce test en démo live, tu as gagné.

---

## 👥 Répartition des Rôles

### 🧑‍💻 Côté Technique (Toi)

**Tu possèdes** (tu codes, débogues, documentes) :

| Tâche | Quand |
| :--- | :--- |
| Structure dépôt + DVC + Pandera | S1 |
| `prepare.py` + `train.py` + MLflow tracking | S2 |
| `@champion` dans le Registry | S3 |
| `api/main.py` + `api/security.py` (FastAPI + API Key) | S4 |
| `Dockerfile` + `docker-compose.yml` | S5 |
| `drift_report.py` (Evidently + seuils) | S6 |
| `test_skew.py` dans la CI | S7 |
| `ci.yml` (lint, tests, build) | S9 |
| `retrain.yml` (3 déclencheurs + concurrency) + `retrain.py` | S10 |
| `gate.py` (comparaison + flip d'alias) | S11 |
| Dashboard Gradio + déploiement HF Spaces | S12 |
| Rollback + audit trail JSONL + `runbook.md` | S13 |

### 📊 Côté Analyse / Storytelling (Ton Ami)

**Il possède** (il produit, rédige, interprète) :

| Tâche | Quand |
| :--- | :--- |
| EDA complète + visualisations | S1 |
| Rédaction des règles Pandera (métier) | S2 |
| Interprétation des métriques (choix du modèle) | S3 |
| Interprétation business du rapport Evidently | S6–S7 |
| Vulgarisation des seuils PSI pour le README | S7 |
| Test du dashboard (feedback UX, clarté) | S12 |
| Rédaction du rapport final | M4 |
| Préparation des slides + répétitions orales | S14–S15 |

### 🔄 Points de Synchronisation

| Quand | Toi → Lui | Lui → Toi |
| :--- | :--- | :--- |
| **S1** | Dataset + structure | EDA + visualisations |
| **S2** | Pipeline préprocessing | Règles Pandera (métier) |
| **S3** | 3 runs MLflow | Note de décision (modèle) |
| **S4** | API locale | Exemples de requêtes JSON |
| **S6** | Rapport Evidently (HTML) | Interprétation business |
| **S7** | Seuils PSI configurés | Vulgarisation pour README |
| **S11** | Gate opérationnel | Métriques à afficher sur dashboard |
| **S12** | Dashboard déployé | Feedback UX + bugs |
| **S13** | Runbook + audit trail | Rapport + slides |

### 📈 Progression d'Apprentissage (Ton Ami)

| Mois | Ce qu'il apprend | Comment |
| :--- | :--- | :--- |
| **M1** | Pandera (validation) | Tu montres 2–3 exemples, il écrit les règles métier |
| **M2** | Lire un rapport Evidently + métriques (F1, PR-AUC) | Tu expliques, il interprète |
| **M3** | MLflow UI + tester une API avec `curl` | Tu montres, il exécute |
| **M4** | Lire un workflow GitHub Actions | Tu montres les logs, il identifie les étapes |

**Règle d'or** : à chaque brique technique produite, **10 min d'explication**. C'est ce qui fera de lui un vrai analyste MLOps, pas juste un rédacteur.

---

## ⚖️ Équilibre de la Charge

| Mois | Toi (technique) | Lui (analyse) |
| :--- | :--- | :--- |
| **M1** | ~70 % | ~30 % |
| **M2** | ~70 % | ~30 % |
| **M3** | ~80 % | ~20 % |
| **M4** | ~40 % | ~60 % |

**Pourquoi ce déséquilibre est normal** : M1–M3 sont intensifs en code (tu portes la charge). M4 est intensif en rédaction et oral (il porte la charge). C'est un **binôme en relais**, pas en parallèle strict.

---

## 🚫 Ce Que Chacun Ne Fait PAS

| Tâche | Ne pas faire | Pourquoi |
| :--- | :--- | :--- |
| **Code MLOps** | Ton ami ne code pas Docker/CI/CD/MLflow/gate | Risque de casser un pipeline non compris |
| **Rapport final** | Tu ne rédiges pas à sa place | C'est son terrain, il sait structurer un récit |
| **Choix du modèle** | Tu ne choisis pas seul | Il doit pouvoir justifier avec les métriques |
| **Cloud Azure** | Ton ami ne touche pas au cloud | Risque d'épuiser le crédit |
| **UX du dashboard** | Tu ne décides pas seul | Il est le "testeur utilisateur" |

---

## 💡 Discipline de Périmètre (Facteur de Succès)

**À la fin du Mois 3, 3 questions :**
1. L'API Docker répond en < 200 ms en local ?
2. Un rapport Evidently montre une dérive simulée ?
3. La démo HF Spaces est stable ?

- **3 oui** → durcissement du gate (rollback, audit) sur 2 semaines max.
- **2 oui ou moins** → abandonner le durcissement **sans culpabilité**. Sécuriser rapport + soutenance.

Le socle est déjà un projet complet et crédible. L'extension est un **bonus conditionnel**.

---

## 📌 En Une Phrase

**Toi :** "Je construis un système ML qui se déploie, se surveille et se ré-entraîne tout seul, avec un gate qui empêche les régressions."

**Lui :** "Je raconte l'histoire de ce système : pourquoi il existe, ce qu'il fait, et ce que les données disent."

**Ensemble :** un projet qui montre **le cycle de vie complet** d'un modèle ML — de l'analyse à la production — avec une vraie maîtrise du MLOps.