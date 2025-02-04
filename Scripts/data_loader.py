"""
Chargement et préparation des données depuis SQLite
"""

import pandas as pd
import numpy as np
import sqlite3
from typing import Tuple
import logging
from config import DB_PATH, EXPECTED_COLUMNS
import atexit

logger = logging.getLogger(__name__)

# Variable globale pour la connexion
_connection = None

def get_db_connection():
    """
    Établit une connexion à la base de données SQLite
    """
    global _connection
    
    if _connection is None:
        logger.info(f"Tentative de connexion à la base de données: {DB_PATH}")
        try:
            _connection = sqlite3.connect(DB_PATH)
            # Configuration de la connexion
            _connection.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
            _connection.execute("PRAGMA synchronous=NORMAL")  # Meilleur compromis performance/sécurité
            
            # Vérifier que la connexion fonctionne
            cursor = _connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions")
            count = cursor.fetchone()[0]
            logger.info(f"Connexion réussie. Nombre de transactions: {count}")
        except Exception as e:
            logger.error(f"Erreur de connexion à la base de données: {str(e)}")
            raise
    
    return _connection

def close_connection():
    """
    Ferme proprement la connexion à la base de données
    """
    global _connection
    if _connection is not None:
        logger.info("Fermeture de la connexion à la base de données")
        try:
            _connection.close()
            _connection = None
        except Exception as e:
            logger.error(f"Erreur lors de la fermeture de la connexion: {str(e)}")

# S'assurer que la connexion est fermée à la fin du programme
atexit.register(close_connection)

def load_data() -> pd.DataFrame:
    """
    Charge les données depuis la base SQLite
    
    Returns:
        DataFrame contenant les données nettoyées
    """
    logger.info("Chargement des données depuis SQLite")
    
    try:
        query = """
        SELECT step, customer, age, gender, merchant, category,
               amount, fraud
        FROM transactions
        """
        
        conn = get_db_connection()
        logger.info("Exécution de la requête SQL")
        df = pd.read_sql_query(query, conn)
        logger.info(f"Données chargées avec succès: {len(df)} lignes")
        
        # Vérification des colonnes
        missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Colonnes manquantes dans le dataset: {missing_cols}")
        
        # Nettoyage des données
        df = clean_data(df)
        
        logger.info(f"Données chargées et nettoyées avec succès: {len(df)} lignes")
        return df
    
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données: {str(e)}")
        raise

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et prépare les données
    """
    # Copie pour éviter les modifications sur le DataFrame original
    df = df.copy()
    
    # Conversion des types
    df['step'] = pd.to_numeric(df['step'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['fraud'] = df['fraud'].astype(int)
    
    # Nettoyage des valeurs manquantes
    df = df.dropna(subset=['amount', 'step'])
    
    # Conversion des catégories en type category pour optimisation
    categorical_columns = ['customer', 'merchant', 'category', 'gender']
    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    return df

def get_data_info() -> dict:
    """
    Retourne des informations de base sur le dataset
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Statistiques générales
        stats = {}
        
        # Nombre total de transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        stats['total_transactions'] = cursor.fetchone()[0]
        
        # Nombre de clients uniques
        cursor.execute("SELECT COUNT(DISTINCT customer) FROM transactions")
        stats['unique_customers'] = cursor.fetchone()[0]
        
        # Nombre de commerçants uniques
        cursor.execute("SELECT COUNT(DISTINCT merchant) FROM transactions")
        stats['unique_merchants'] = cursor.fetchone()[0]
        
        # Montant total
        cursor.execute("SELECT SUM(amount) FROM transactions")
        stats['total_amount'] = cursor.fetchone()[0]
        
        # Statistiques sur les fraudes
        cursor.execute("""
            SELECT COUNT(*) as fraud_count,
                   (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions)) as fraud_rate
            FROM transactions
            WHERE fraud = 1
        """)
        fraud_count, fraud_rate = cursor.fetchone()
        stats['fraud_count'] = fraud_count
        stats['fraud_rate'] = round(fraud_rate, 2)
        
        return stats
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations: {str(e)}")
        raise

def execute_query(query: str) -> pd.DataFrame:
    """
    Exécute une requête SQL et retourne les résultats dans un DataFrame
    """
    try:
        conn = get_db_connection()
        return pd.read_sql_query(query, conn)
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de la requête: {str(e)}")
        raise
