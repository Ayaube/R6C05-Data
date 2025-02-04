"""
Analyses descriptives des données
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging
from utils import save_results
from data_loader import execute_query
from config import AMOUNT_BINS, AMOUNT_LABELS

logger = logging.getLogger(__name__)

def perform_descriptive_analysis(df: pd.DataFrame = None) -> Dict[str, pd.DataFrame]:
    """
    Réalise l'ensemble des analyses descriptives
    
    Returns:
        Dict contenant les différents DataFrames d'analyse
    """
    logger.info("Début de l'analyse descriptive")
    results = {}
    
    # Analyse par catégorie
    results['category_analysis'] = analyze_by_category()
    
    # Analyse des montants
    results['amount_analysis'] = analyze_amounts()
    
    # Analyse démographique
    results['demographic_analysis'] = analyze_demographics()
    
    # Sauvegarde des résultats
    for name, result_df in results.items():
        save_results(result_df, f"descriptive_{name}")
    
    logger.info("Analyse descriptive terminée")
    return results

def analyze_by_category() -> pd.DataFrame:
    """
    Analyse des transactions par catégorie
    """
    query = """
    SELECT 
        category,
        COUNT(*) as total_transactions,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount,
        SUM(CASE WHEN fraud = 1 THEN 1 ELSE 0 END) as fraud_count,
        (SUM(CASE WHEN fraud = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as fraud_rate
    FROM transactions
    GROUP BY category
    ORDER BY total_transactions DESC
    """
    
    category_stats = execute_query(query)
    category_stats['fraud_rate'] = category_stats['fraud_rate'].round(2)
    
    return category_stats

def analyze_amounts() -> pd.DataFrame:
    """
    Analyse de la distribution des montants
    """
    query = """
    WITH amount_categories AS (
        SELECT 
            CASE 
                WHEN amount <= 100 THEN '0-100'
                WHEN amount <= 500 THEN '100-500'
                WHEN amount <= 1000 THEN '500-1000'
                WHEN amount <= 2000 THEN '1000-2000'
                WHEN amount <= 5000 THEN '2000-5000'
                ELSE '>5000'
            END as amount_category,
            amount,
            fraud
        FROM transactions
    )
    SELECT 
        amount_category,
        COUNT(*) as transaction_count,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount,
        SUM(fraud) as fraud_count,
        (SUM(fraud) * 100.0 / COUNT(*)) as fraud_rate
    FROM amount_categories
    GROUP BY amount_category
    ORDER BY 
        CASE amount_category
            WHEN '0-100' THEN 1
            WHEN '100-500' THEN 2
            WHEN '500-1000' THEN 3
            WHEN '1000-2000' THEN 4
            WHEN '2000-5000' THEN 5
            WHEN '>5000' THEN 6
        END
    """
    
    amount_stats = execute_query(query)
    amount_stats['fraud_rate'] = amount_stats['fraud_rate'].round(2)
    
    return amount_stats

def analyze_demographics() -> pd.DataFrame:
    """
    Analyse démographique des transactions
    """
    query = """
    SELECT 
        age,
        gender,
        COUNT(*) as transaction_count,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount,
        SUM(fraud) as fraud_count,
        (SUM(fraud) * 100.0 / COUNT(*)) as fraud_rate
    FROM transactions
    GROUP BY age, gender
    ORDER BY age, gender
    """
    
    demo_stats = execute_query(query)
    demo_stats['fraud_rate'] = demo_stats['fraud_rate'].round(2)
    
    return demo_stats
