# Analyse des Données Bancaires 🏦

Ce projet contient un ensemble de scripts Python pour analyser les données bancaires du dataset BankSim, avec un focus particulier sur la détection des fraudes et l'analyse des patterns de transaction.

## Structure du Projet 📁

- `config.py` : Configuration globale et constantes
- `utils.py` : Fonctions utilitaires communes
- `data_loader.py` : Chargement et préparation des données
- `descriptive_analysis.py` : Analyses descriptives
- `temporal_analysis.py` : Analyses temporelles
- `fraud_analysis.py` : Analyses des fraudes
- `anomaly_detection.py` : Détection d'anomalies
- `visualization.py` : Fonctions de visualisation
- `main.py` : Script principal

## Installation 🛠️

1. Créez un environnement virtuel Python :
```bash
python -m venv venv
source venv/bin/activate  # Sur Unix
# ou
venv\Scripts\activate  # Sur Windows
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation 🚀

Pour lancer l'analyse complète, exécutez :
```bash
python main.py
```

## Résultats 📊

Les résultats de l'analyse seront sauvegardés dans deux dossiers :
- `Results/` : Fichiers CSV contenant les analyses détaillées
- `Results/Figures/` : Visualisations générées au format PNG

## Analyses Réalisées 📈

1. **Analyse Descriptive**
   - Statistiques générales
   - Distribution des transactions par catégorie
   - Analyse des montants

2. **Analyse Temporelle**
   - Patterns quotidiens
   - Identification des périodes à risque

3. **Analyse des Fraudes**
   - Profil des transactions frauduleuses
   - Analyse par montant
   - Analyse par commerçant
   - Analyse par catégorie

4. **Détection d'Anomalies**
   - Transactions suspectes
   - Comportements clients anormaux
   - Marchands à risque

## Notes 📝

- Le script utilise par défaut le fichier complet (`big.csv`). Pour utiliser le petit dataset, modifiez `use_small=True` dans `main.py`
- Les seuils de détection d'anomalies peuvent être ajustés dans `anomaly_detection.py`
- Les paramètres de visualisation peuvent être modifiés dans `config.py`
