"""
Détection d'anomalies dans les transactions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from scipy import stats
from utils import save_results

logger = logging.getLogger(__name__)

def perform_anomaly_detection(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Réalise l'ensemble des analyses de détection d'anomalies
    
    Returns:
        Dict contenant les différents DataFrames d'analyse
    """
    logger.info("Début de la détection d'anomalies")
    results = {}
    
    # Détection des transactions anormales
    results['transaction_anomalies'] = detect_transaction_anomalies(df)
    
    # Détection des comportements clients suspects
    results['customer_anomalies'] = detect_customer_anomalies(df)
    
    # Détection des comportements marchands suspects
    results['merchant_anomalies'] = detect_merchant_anomalies(df)
    
    # Sauvegarde des résultats
    for name, result_df in results.items():
        save_results(result_df, f"anomaly_{name}")
    
    logger.info("Détection d'anomalies terminée")
    return results

def detect_transaction_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Détecte les anomalies au niveau des transactions
    """
    # Calculer les statistiques par catégorie
    category_stats = df.groupby('category', observed=True).agg({
        'amount': ['mean', 'std']
    })
    
    # Aplatir les colonnes multi-index
    category_stats.columns = ['mean_amount', 'std_amount']
    
    # Fusionner avec le DataFrame original
    df_with_stats = df.merge(category_stats, left_on='category', right_index=True)
    
    # Calculer le z-score pour chaque transaction
    df_with_stats['amount_zscore'] = (df_with_stats['amount'] - df_with_stats['mean_amount']) / df_with_stats['std_amount']
    
    # Identifier les anomalies (z-score > 3 ou < -3)
    anomalies = df_with_stats[
        (abs(df_with_stats['amount_zscore']) > 3)
    ].copy()
    
    # Ajouter une colonne pour le type d'anomalie
    anomalies['anomaly_type'] = np.where(
        anomalies['amount_zscore'] > 3,
        'montant_élevé',
        'montant_faible'
    )
    
    # Sélectionner et renommer les colonnes pertinentes
    result = anomalies[[
        'step', 'customer', 'age', 'gender', 'merchant', 'category',
        'amount', 'fraud', 'amount_zscore', 'anomaly_type'
    ]].copy()
    
    result = result.sort_values('amount_zscore', ascending=False)
    
    return result

def detect_customer_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Détecte les anomalies au niveau des clients
    """
    # Calculer les statistiques par client
    customer_stats = df.groupby('customer', observed=True).agg({
        'amount': ['count', 'mean', 'sum'],
        'fraud': 'sum'
    })
    
    # Aplatir les colonnes multi-index
    customer_stats.columns = ['transaction_count', 'avg_amount', 'total_amount', 'fraud_count']
    
    # Calculer les z-scores pour chaque métrique
    for col in ['transaction_count', 'avg_amount', 'total_amount']:
        mean = customer_stats[col].mean()
        std = customer_stats[col].std()
        customer_stats[f'{col}_zscore'] = (customer_stats[col] - mean) / std
    
    # Identifier les clients avec des comportements anormaux
    anomalies = customer_stats[
        (abs(customer_stats['transaction_count_zscore']) > 3) |
        (abs(customer_stats['avg_amount_zscore']) > 3) |
        (abs(customer_stats['total_amount_zscore']) > 3) |
        (customer_stats['fraud_count'] > 0)
    ].copy()
    
    # Déterminer le type d'anomalie principal
    def get_anomaly_type(row):
        if row['fraud_count'] > 0:
            return 'fraude_détectée'
        elif abs(row['transaction_count_zscore']) > 3:
            return 'nombre_transactions_anormal'
        elif abs(row['avg_amount_zscore']) > 3:
            return 'montant_moyen_anormal'
        else:
            return 'montant_total_anormal'
    
    anomalies['anomaly_type'] = anomalies.apply(get_anomaly_type, axis=1)
    
    # Trier par gravité d'anomalie
    anomalies = anomalies.sort_values(
        ['fraud_count', 'transaction_count_zscore', 'total_amount_zscore'],
        ascending=[False, False, False]
    )
    
    return anomalies

def detect_merchant_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Détecte les anomalies au niveau des commerçants
    """
    # Calculer les statistiques par commerçant
    merchant_stats = df.groupby('merchant', observed=True).agg({
        'amount': ['count', 'mean', 'sum'],
        'fraud': ['sum', lambda x: (x.sum() / len(x)) * 100]
    })
    
    # Aplatir les colonnes multi-index
    merchant_stats.columns = [
        'transaction_count', 'avg_amount', 'total_amount',
        'fraud_count', 'fraud_rate'
    ]
    
    # Calculer les z-scores pour chaque métrique
    for col in ['transaction_count', 'avg_amount', 'total_amount', 'fraud_rate']:
        mean = merchant_stats[col].mean()
        std = merchant_stats[col].std()
        merchant_stats[f'{col}_zscore'] = (merchant_stats[col] - mean) / std
    
    # Identifier les commerçants avec des comportements anormaux
    anomalies = merchant_stats[
        (abs(merchant_stats['transaction_count_zscore']) > 3) |
        (abs(merchant_stats['avg_amount_zscore']) > 3) |
        (abs(merchant_stats['total_amount_zscore']) > 3) |
        (merchant_stats['fraud_rate_zscore'] > 3)
    ].copy()
    
    # Déterminer le type d'anomalie principal
    def get_anomaly_type(row):
        if row['fraud_rate_zscore'] > 3:
            return 'taux_fraude_élevé'
        elif abs(row['transaction_count_zscore']) > 3:
            return 'nombre_transactions_anormal'
        elif abs(row['avg_amount_zscore']) > 3:
            return 'montant_moyen_anormal'
        else:
            return 'montant_total_anormal'
    
    anomalies['anomaly_type'] = anomalies.apply(get_anomaly_type, axis=1)
    
    # Trier par gravité d'anomalie
    anomalies = anomalies.sort_values(
        ['fraud_rate_zscore', 'transaction_count_zscore', 'total_amount_zscore'],
        ascending=[False, False, False]
    )
    
    return anomalies
