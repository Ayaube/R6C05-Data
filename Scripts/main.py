"""
Script principal pour l'analyse des données bancaires
"""

import logging
from pathlib import Path
import time
import pandas as pd
from typing import Dict

from config import (
    LOGGING_FORMAT,
    LOGGING_LEVEL,
    RESULTS_DIR
)

from data_loader import load_data, get_data_info
from descriptive_analysis import perform_descriptive_analysis
from temporal_analysis import perform_temporal_analysis
from fraud_analysis import perform_fraud_analysis
from anomaly_detection import perform_anomaly_detection
from visualization import generate_visualizations
from generate_kpi_dashboard import create_kpi_dashboard
from temporal_patterns_analysis import analyze_temporal_patterns
from cycle_analysis import analyze_cycles
from amount_distribution_analysis import analyze_amount_distribution

# Configuration du logging
logging.basicConfig(
    level=LOGGING_LEVEL,
    format=LOGGING_FORMAT
)

logger = logging.getLogger(__name__)

def format_results_summary(info: pd.Series, temporal_stats: dict, cycle_stats: dict, amount_stats: dict) -> str:
    """
    Formate le résumé des résultats pour l'affichage
    """
    return f"""
Résumé de l'analyse :

1. Statistiques Générales
------------------------
Nombre total de transactions : {info['total_transactions']:,}
Taux de fraude global : {info['fraud_rate']:.2f}%
Montant total des transactions : {info['total_amount']:,.2f} €

2. Patterns Temporels
--------------------
Jour le plus actif : {temporal_stats['Jour le plus actif']:.0f} ({temporal_stats['Nombre max de transactions']:,.0f} transactions)
Jour avec le plus haut taux de fraude : {temporal_stats['Jour le plus risqué']:.0f} ({temporal_stats['Taux de fraude max']:.2f}%)
Montant moyen des transactions : {temporal_stats['Montant moyen global']:.2f} €

3. Analyse des Cycles
--------------------
Distance moyenne entre les pics : {cycle_stats['distance_moyenne_pics']:.1f} jours
Jour le plus actif : {cycle_stats['jour_plus_actif']}
Jour le moins actif : {cycle_stats['jour_moins_actif']}
Variation hebdomadaire : {cycle_stats['variation_hebdomadaire']:.1f}%

4. Distribution des Montants
---------------------------
Montant minimum : {amount_stats['minimum']:.2f} €
Montant maximum : {amount_stats['maximum']:.2f} € ({amount_stats['max_categorie']})
Montant médian : {amount_stats['mediane']:.2f} €
{amount_stats['pct_inf_100']:.1f}% des transactions ≤ 100€
Asymétrie : {amount_stats['skewness']:.2f} (distribution très asymétrique)

Les résultats détaillés ont été sauvegardés dans : {RESULTS_DIR}
Les visualisations ont été sauvegardées dans : {RESULTS_DIR / 'Figures'}
"""

def main():
    """
    Fonction principale qui orchestre l'analyse
    """
    start_time = time.time()
    
    logger.info("Début de l'analyse des données bancaires")
    
    # Chargement des données
    df = load_data()
    
    # Informations de base sur le dataset
    info = get_data_info()
    logger.info(f"Informations sur le dataset :\n{pd.Series(info)}")
    
    try:
        # Analyse descriptive
        descriptive_results = perform_descriptive_analysis(df)
        
        # Analyse temporelle
        temporal_results = perform_temporal_analysis(df)
        
        # Analyse des fraudes
        fraud_results = perform_fraud_analysis(df)
        
        # Détection d'anomalies
        anomaly_results = perform_anomaly_detection(df)
        
        # Génération des visualisations de base
        logger.info("Génération des visualisations de base")
        generate_visualizations(df, RESULTS_DIR)
        
        # Génération du dashboard KPI
        logger.info("Génération du dashboard KPI")
        create_kpi_dashboard()
        
        # Analyse des patterns temporels
        logger.info("Analyse des patterns temporels")
        temporal_stats = analyze_temporal_patterns()
        
        # Analyse des cycles
        logger.info("Analyse des cycles")
        cycle_stats = analyze_cycles()
        
        # Analyse de la distribution des montants
        logger.info("Analyse de la distribution des montants")
        amount_stats = analyze_amount_distribution()
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse : {str(e)}")
        raise
    
    # Afficher le résumé
    execution_time = time.time() - start_time
    logger.info(f"Analyse terminée en {execution_time:.2f} secondes")
    print(format_results_summary(pd.Series(info), temporal_stats, cycle_stats, amount_stats))

if __name__ == "__main__":
    main()
