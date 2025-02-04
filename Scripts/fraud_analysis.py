"""
Analyses spécifiques aux transactions frauduleuses
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging
from utils import calculate_fraud_rate, save_results
from config import AMOUNT_BINS, AMOUNT_LABELS

logger = logging.getLogger(__name__)

def perform_fraud_analysis(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Réalise l'ensemble des analyses sur les fraudes
    
    Returns:
        Dict contenant les différents DataFrames d'analyse
    """
    logger.info("Début de l'analyse des fraudes")
    results = {}
    
    # Analyse par montant
    results['amount_fraud'] = analyze_fraud_by_amount(df)
    
    # Analyse par commerçant
    results['merchant_fraud'] = analyze_merchant_risk(df)
    
    # Analyse par catégorie de commerce
    results['category_fraud'] = analyze_category_risk(df)
    
    # Analyse démographique des fraudes
    if 'age' in df.columns and 'gender' in df.columns:
        results['demographic_fraud'] = analyze_demographic_risk(df)
    
    # Sauvegarde des résultats
    for name, result_df in results.items():
        save_results(result_df, f"fraud_{name}")
    
    logger.info("Analyse des fraudes terminée")
    return results

def analyze_fraud_by_amount(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse des fraudes par tranche de montant
    """
    df['amount_category'] = pd.cut(df['amount'], 
                                 bins=AMOUNT_BINS,
                                 labels=AMOUNT_LABELS)
    
    # Statistiques générales par tranche de montant
    amount_fraud = df.groupby('amount_category', observed=True).agg({
        'amount': ['count', 'sum', 'mean'],
        'fraud': ['sum', 'mean']
    }).round(2)
    
    amount_fraud.columns = ['transaction_count', 'total_amount', 'avg_amount',
                          'fraud_count', 'fraud_rate']
    amount_fraud['fraud_rate'] = (amount_fraud['fraud_rate'] * 100).round(2)
    
    return amount_fraud

def analyze_merchant_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse du risque par commerçant
    """
    # Calcul des statistiques par commerçant
    merchant_stats = df.groupby('merchant', observed=True).agg({
        'amount': ['count', 'sum', 'mean'],
        'fraud': ['sum', 'mean']
    }).round(2)
    
    merchant_stats.columns = ['transaction_count', 'total_amount', 'avg_amount',
                            'fraud_count', 'fraud_rate']
    merchant_stats['fraud_rate'] = (merchant_stats['fraud_rate'] * 100).round(2)
    
    # Identification des commerçants à haut risque
    threshold = merchant_stats['fraud_rate'].mean() + merchant_stats['fraud_rate'].std()
    merchant_stats['is_high_risk'] = merchant_stats['fraud_rate'] > threshold
    
    return merchant_stats.sort_values('fraud_rate', ascending=False)

def analyze_category_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse du risque par catégorie de commerce
    """
    # Calcul des statistiques par catégorie
    category_stats = df.groupby('category', observed=True).agg({
        'amount': ['count', 'sum', 'mean'],
        'fraud': ['sum', 'mean']
    }).round(2)
    
    category_stats.columns = ['transaction_count', 'total_amount', 'avg_amount',
                            'fraud_count', 'fraud_rate']
    category_stats['fraud_rate'] = (category_stats['fraud_rate'] * 100).round(2)
    
    # Calcul des indices de risque relatif
    avg_fraud_rate = df['fraud'].mean() * 100
    category_stats['risk_index'] = (category_stats['fraud_rate'] / avg_fraud_rate).round(2)
    
    return category_stats.sort_values('risk_index', ascending=False)

def analyze_demographic_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse du risque par segment démographique
    """
    # Calcul des statistiques par âge et genre
    demo_stats = df.groupby(['age', 'gender'], observed=True).agg({
        'amount': ['count', 'sum', 'mean'],
        'fraud': ['sum', 'mean']
    }).round(2)
    
    demo_stats.columns = ['transaction_count', 'total_amount', 'avg_amount',
                         'fraud_count', 'fraud_rate']
    demo_stats['fraud_rate'] = (demo_stats['fraud_rate'] * 100).round(2)
    
    return demo_stats.sort_values('fraud_rate', ascending=False)
