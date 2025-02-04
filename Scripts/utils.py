"""
Fonctions utilitaires pour l'analyse des données
"""

import pandas as pd
import numpy as np
from typing import Union, List, Dict
import logging
from datetime import datetime
from config import RESULTS_DIR

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(RESULTS_DIR / 'analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def calculate_fraud_rate(data: pd.DataFrame, group_by: Union[str, List[str]]) -> pd.DataFrame:
    """
    Calcule le taux de fraude par groupe spécifié
    """
    fraud_rate = (data
                 .groupby(group_by)
                 .agg({
                     'fraud': ['count', 'sum']
                 })
                 .reset_index())
    
    fraud_rate.columns = [group_by] if isinstance(group_by, str) else group_by + ['total', 'frauds']
    if isinstance(group_by, str):
        fraud_rate['total'] = fraud_rate['count']
        fraud_rate['frauds'] = fraud_rate['sum']
    
    fraud_rate['fraud_rate'] = (fraud_rate['frauds'] / fraud_rate['total'] * 100).round(2)
    return fraud_rate

def save_results(df: pd.DataFrame, name: str, index: bool = False) -> None:
    """
    Sauvegarde les résultats dans un fichier CSV
    """
    output_path = RESULTS_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(output_path, index=index)
    logger.info(f"Résultats sauvegardés dans {output_path}")

def format_amount(amount: float) -> str:
    """
    Formate les montants pour l'affichage
    """
    return f"{amount:,.2f} €"
