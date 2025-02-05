"""
Analyse de la corrélation entre les montants et les fraudes
"""

import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
DB_PATH = Path(__file__).parent.parent / 'SQLite' / 'bankdata.db'
RESULTS_DIR = Path(__file__).parent.parent / 'Results'
FIGURES_DIR = RESULTS_DIR / 'Figures'
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def get_fraud_amount_data():
    """Récupère les données pour l'analyse"""
    # Requête pour les tranches
    tranche_query = """
    WITH amount_ranges AS (
        SELECT 
            CASE 
                WHEN amount <= 10 THEN '0-10€'
                WHEN amount <= 20 THEN '10-20€'
                WHEN amount <= 50 THEN '20-50€'
                WHEN amount <= 100 THEN '50-100€'
                WHEN amount <= 200 THEN '100-200€'
                WHEN amount <= 500 THEN '200-500€'
                WHEN amount <= 1000 THEN '500-1000€'
                ELSE '> 1000€'
            END AS tranche_montant,
            fraud,
            amount,
            category
        FROM transactions
    )
    SELECT 
        tranche_montant,
        COUNT(*) as total_transactions,
        SUM(fraud) as fraudulent_transactions,
        ROUND(AVG(fraud) * 100, 2) as fraud_rate,
        ROUND(AVG(amount), 2) as avg_amount,
        ROUND(MIN(amount), 2) as min_amount,
        ROUND(MAX(amount), 2) as max_amount
    FROM amount_ranges
    GROUP BY tranche_montant
    ORDER BY min_amount;
    """
    
    # Requête pour les données brutes (pour la corrélation)
    correlation_query = """
    SELECT amount, fraud
    FROM transactions;
    """
    
    with sqlite3.connect(DB_PATH) as conn:
        tranche_data = pd.read_sql_query(tranche_query, conn)
        correlation_data = pd.read_sql_query(correlation_query, conn)
    
    return tranche_data, correlation_data

def analyze_fraud_amount_correlation():
    """Analyse et visualise la corrélation entre montants et fraudes"""
    # Récupération des données
    data, raw_data = get_fraud_amount_data()
    
    # Configuration de la figure
    plt.style.use('default')
    sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(15, 12))  # Augmentation de la hauteur
    
    # 1. Taux de fraude par tranche de montant
    ax1 = plt.subplot(2, 1, 1)
    
    # Créer le graphique en barres
    bars = ax1.bar(range(len(data)), data['fraud_rate'], color='lightcoral')
    
    # Ajouter les étiquettes
    ax1.set_xticks(range(len(data)))
    ax1.set_xticklabels(data['tranche_montant'], rotation=45, ha='right')
    
    # Ajouter les valeurs sur les barres
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,  # Déplacement vers le haut
                f'{height:.1f}%', ha='center', va='bottom')
    
    # Ajouter le nombre de transactions en dessous des étiquettes
    ax1.text(-0.2, -5, 'Nombre de\ntransactions:', ha='right')  # Légende
    for i, transactions in enumerate(data['total_transactions']):
        ax1.text(i, -5, f'{transactions:,}', ha='center', rotation=0)  # Rotation à 0
    
    ax1.set_title('Taux de Fraude par Tranche de Montant')
    ax1.set_ylabel('Taux de Fraude (%)')
    
    # Ajuster les limites pour accommoder les étiquettes
    ax1.set_ylim(-10, max(data['fraud_rate']) * 1.2)  # Augmentation de la marge
    
    # 2. Distribution des fraudes par tranche de montant
    ax2 = plt.subplot(2, 1, 2)
    
    # Calculer la distribution des fraudes
    data['fraud_distribution'] = (data['fraudulent_transactions'] / 
                                data['fraudulent_transactions'].sum() * 100)
    
    # Créer le graphique en barres
    bars = ax2.bar(range(len(data)), data['fraud_distribution'], color='lightblue')
    
    # Ajouter les étiquettes
    ax2.set_xticks(range(len(data)))
    ax2.set_xticklabels(data['tranche_montant'], rotation=45, ha='right')
    
    # Ajouter les valeurs sur les barres
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,  # Déplacement vers le haut
                f'{height:.1f}%', ha='center', va='bottom')
    
    # Ajouter le nombre de fraudes en dessous des étiquettes
    ax2.text(-0.2, -2, 'Nombre de\nfraudes:', ha='right')  # Légende
    for i, frauds in enumerate(data['fraudulent_transactions']):
        ax2.text(i, -2, f'{frauds:,}', ha='center', rotation=0)  # Rotation à 0
    
    ax2.set_title('Distribution des Fraudes par Tranche de Montant')
    ax2.set_ylabel('Pourcentage des Fraudes Totales (%)')
    
    # Ajuster les limites pour accommoder les étiquettes
    ax2.set_ylim(-4, max(data['fraud_distribution']) * 1.2)  # Augmentation de la marge
    
    # Ajustements finaux
    plt.tight_layout(rect=[0, 0, 1, 1])  # Ajustement des marges sans titre
    
    # Sauvegarde
    plt.savefig(FIGURES_DIR / 'fraud_amount_correlation.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    # Calcul des statistiques
    stats = {
        # Corrélation point-bisériale (entre variable continue et binaire)
        'correlation': raw_data['amount'].corr(raw_data['fraud']),
        'correlation_spearman': raw_data['amount'].corr(raw_data['fraud'], method='spearman'),
        'tranche_plus_risquee': data.iloc[data['fraud_rate'].idxmax()]['tranche_montant'],
        'taux_max': data['fraud_rate'].max(),
        'tranche_plus_fraudee': data.iloc[data['fraudulent_transactions'].idxmax()]['tranche_montant'],
        'nb_fraudes_max': data['fraudulent_transactions'].max()
    }
    
    return stats

if __name__ == '__main__':
    stats = analyze_fraud_amount_correlation()
    print("\nStatistiques sur la relation montants-fraudes :")
    print(f"• Corrélation de Pearson : {stats['correlation']:.3f}")
    print(f"• Corrélation de Spearman : {stats['correlation_spearman']:.3f}")
    print(f"• Tranche la plus risquée : {stats['tranche_plus_risquee']} ({stats['taux_max']:.1f}% de fraudes)")
    print(f"• Tranche avec le plus de fraudes : {stats['tranche_plus_fraudee']} ({stats['nb_fraudes_max']:,} fraudes)")
