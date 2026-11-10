# 🚀 Churn Sentinel — MLOps Pipeline with Automated Retraining

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![MLflow](https://img.shields.io/badge/MLflow-2.x-blue)](https://mlflow.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue)](https://www.docker.com/)

> **Un système de prédiction du churn client qui ne se contente pas d'être précis : il est fiable, observable et capable de se maintenir tout seul à jour.**

---

## 🎯 Le Problème

La plupart des projets de data science s'arrêtent au notebook. Un modèle qui atteint 94 % d'accuracy en local peut passer à 71 % en production sans qu'aucune alerte ne se déclenche. C'est **l'échec silencieux** — la cause n°1 des défaillances ML en production.

**Churn Sentinel** résout ce problème en traitant le **cycle de vie complet** d'un modèle :
- De l'analyse des données à la mise en production.
- Du monitoring de dérive au ré-entraînement automatisé.

---

## 🏗️ Architecture

Le projet sépare deux boucles :

- **Boucle Interne (Inner Loop)** : expérimentation, EDA, entraînement, comparaison de modèles.
- **Boucle Externe (Outer Loop)** : serving, monitoring, ré-entraînement, gate de promotion, rollback.

**Le pont entre les deux est le Registre MLflow**, qui stocke le modèle et ses métadonnées (hash DVC, commit Git, hyperparamètres) — rendant le rollback possible en un seul appel API.
