"""
Analyses temporelles des transactions
"""

import pandas as pd
import numpy as np
from typing import Dict
import logging
from utils import calculate_fraud_rate, save_results

logger = logging.getLogger(__name__)

def perform_temporal_analysis(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Réalise l'ensemble des analyses temporelles
    
    Returns:
        Dict contenant les différents DataFrames d'analyse
    """
    logger.info("Début de l'analyse temporelle")
    results = {}
    
    # Analyse par step (jour)
    results['daily_analysis'] = analyze_daily_patterns(df)
    
    # Analyse des tendances de fraude
    results['fraud_temporal'] = analyze_fraud_patterns(df)
    
    # Sauvegarde des résultats
    for name, result_df in results.items():
        save_results(result_df, f"temporal_{name}")
    
    logger.info("Analyse temporelle terminée")
    return results

def analyze_daily_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse des patterns quotidiens
    """
    daily_stats = df.groupby('step').agg({
        'amount': ['count', 'sum', 'mean'],
        'fraud': ['sum', 'mean']
    }).round(2)
    
    daily_stats.columns = ['transaction_count', 'total_amount', 'avg_amount',
                          'fraud_count', 'fraud_rate']
    daily_stats['fraud_rate'] = (daily_stats['fraud_rate'] * 100).round(2)
    
    # Calcul des moyennes mobiles pour identifier les tendances
    window_size = 7  # fenêtre d'une semaine
    daily_stats['moving_avg_transactions'] = daily_stats['transaction_count'].rolling(window=window_size).mean()
    daily_stats['moving_avg_fraud_rate'] = daily_stats['fraud_rate'].rolling(window=window_size).mean()
    
    return daily_stats

def analyze_fraud_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse des patterns de fraude dans le temps
    """
    # Séparation des transactions frauduleuses et normales
    fraud_df = df[df['fraud'] == 1]
    normal_df = df[df['fraud'] == 0]
    
    # Analyse comparative des distributions temporelles
    fraud_temporal = pd.DataFrame({
        'total_transactions': df.groupby('step').size(),
        'fraud_transactions': fraud_df.groupby('step').size(),
        'normal_transactions': normal_df.groupby('step').size()
    }).fillna(0)
    
    # Calcul des proportions
    fraud_temporal['fraud_rate'] = (fraud_temporal['fraud_transactions'] / 
                                  fraud_temporal['total_transactions'] * 100).round(2)
    
    # Identification des périodes à haut risque
    fraud_temporal['is_high_risk'] = fraud_temporal['fraud_rate'] > fraud_temporal['fraud_rate'].mean()
    
    return fraud_temporal

def identify_risk_periods(df: pd.DataFrame, window_size: int = 7) -> pd.DataFrame:
    """
    Identifie les périodes à haut risque de fraude
    """
    # Calcul du taux de fraude moyen sur une fenêtre glissante
    risk_analysis = df.groupby('step').agg({
        'fraud': ['count', 'sum']
    })
    
    risk_analysis.columns = ['total_transactions', 'fraud_transactions']
    risk_analysis['fraud_rate'] = (risk_analysis['fraud_transactions'] / 
                                 risk_analysis['total_transactions'] * 100).round(2)
    
    # Calcul de la moyenne mobile du taux de fraude
    risk_analysis['moving_avg_fraud_rate'] = risk_analysis['fraud_rate'].rolling(window=window_size).mean()
    
    # Identification des périodes à risque (taux > moyenne + 1 écart-type)
    threshold = risk_analysis['fraud_rate'].mean() + risk_analysis['fraud_rate'].std()
    risk_analysis['is_high_risk'] = risk_analysis['fraud_rate'] > threshold
    
    return risk_analysis
