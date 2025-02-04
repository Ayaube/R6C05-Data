"""
Analyse des patterns temporels des transactions
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

def get_temporal_stats():
    """Récupère les statistiques temporelles"""
    query = """
    SELECT 
        step,
        COUNT(*) as nb_transactions,
        ROUND(AVG(amount), 2) as montant_moyen,
        ROUND(SUM(amount), 2) as volume_total,
        SUM(fraud) as nb_fraudes,
        ROUND(AVG(fraud) * 100, 2) as taux_fraude
    FROM transactions
    GROUP BY step
    ORDER BY step;
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)

def analyze_temporal_patterns():
    """Analyse et visualise les patterns temporels"""
    # Récupération des données
    temporal_stats = get_temporal_stats()
    
    # Configuration de la figure
    plt.style.use('default')
    sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(2, 2)
    
    # 1. Évolution du nombre de transactions
    ax1 = fig.add_subplot(gs[0, 0])
    sns.lineplot(data=temporal_stats, x='step', y='nb_transactions', ax=ax1)
    ax1.set_title('Évolution du Nombre de Transactions par Jour')
    ax1.set_xlabel('Jour de la simulation')
    ax1.set_ylabel('Nombre de Transactions')
    
    # Ajouter la moyenne mobile sur 7 jours
    rolling_mean = temporal_stats['nb_transactions'].rolling(window=7).mean()
    ax1.plot(temporal_stats['step'], rolling_mean, 'r--', 
             label='Moyenne mobile (7 jours)')
    ax1.legend()
    
    # 2. Évolution du montant moyen
    ax2 = fig.add_subplot(gs[0, 1])
    sns.lineplot(data=temporal_stats, x='step', y='montant_moyen', ax=ax2)
    ax2.set_title('Évolution du Montant Moyen par Jour')
    ax2.set_xlabel('Jour de la simulation')
    ax2.set_ylabel('Montant Moyen (€)')
    
    # 3. Distribution du nombre de transactions
    ax3 = fig.add_subplot(gs[1, 0])
    
    # Calculer les statistiques pour les annotations
    stats = temporal_stats['nb_transactions'].describe()
    
    # Créer l'histogramme avec des paramètres plus précis
    sns.histplot(data=temporal_stats, x='nb_transactions', bins=30, ax=ax3,
                color='lightcoral', stat='count')
    
    # Ajouter les lignes verticales pour les quartiles avec des labels plus clairs
    quartiles = temporal_stats['nb_transactions'].quantile([0.25, 0.5, 0.75])
    colors = ['red', 'green', 'blue']
    labels = [f'Q1: {quartiles[0.25]:.0f}', 
             f'Médiane: {quartiles[0.5]:.0f}', 
             f'Q3: {quartiles[0.75]:.0f}']
    
    for q, c, l in zip(quartiles, colors, labels):
        ax3.axvline(q, color=c, linestyle='--', label=l)
    
    ax3.set_title('Distribution du Nombre de Transactions Quotidiennes')
    ax3.set_xlabel('Nombre de Transactions par Jour')
    ax3.set_ylabel('Nombre de Jours')
    
    # Ajouter des statistiques descriptives dans le titre
    ax3.text(0.02, 0.98, 
             f'Moyenne: {stats["mean"]:.0f}\n'
             f'Écart-type: {stats["std"]:.0f}\n'
             f'Min: {stats["min"]:.0f}\n'
             f'Max: {stats["max"]:.0f}',
             transform=ax3.transAxes,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax3.legend()
    
    # 4. Corrélation transactions/fraudes
    ax4 = fig.add_subplot(gs[1, 1])
    sns.scatterplot(data=temporal_stats, x='nb_transactions', y='nb_fraudes', ax=ax4)
    ax4.set_title('Relation entre Nombre de Transactions et Fraudes')
    ax4.set_xlabel('Nombre de Transactions par Jour')
    ax4.set_ylabel('Nombre de Fraudes')
    
    # Ajouter une ligne de régression
    z = np.polyfit(temporal_stats['nb_transactions'], temporal_stats['nb_fraudes'], 1)
    p = np.poly1d(z)
    ax4.plot(temporal_stats['nb_transactions'], 
             p(temporal_stats['nb_transactions']), 
             "r--", alpha=0.8, label='Tendance')
    
    # Calculer et afficher le coefficient de corrélation
    corr = temporal_stats['nb_transactions'].corr(temporal_stats['nb_fraudes'])
    ax4.text(0.02, 0.98, f'Corrélation: {corr:.2f}',
             transform=ax4.transAxes,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax4.legend()
    
    # Ajustements finaux
    plt.suptitle('Analyse des Patterns Temporels', fontsize=16, y=0.95)
    plt.tight_layout()
    
    # Sauvegarde
    plt.savefig(FIGURES_DIR / 'temporal_patterns_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    # Calcul et affichage des statistiques
    stats = {
        'Montant moyen global': temporal_stats['montant_moyen'].mean(),
        'Jour le plus actif': temporal_stats.loc[temporal_stats['nb_transactions'].idxmax(), 'step'],
        'Nombre max de transactions': temporal_stats['nb_transactions'].max(),
        'Jour le plus risqué': temporal_stats.loc[temporal_stats['taux_fraude'].idxmax(), 'step'],
        'Taux de fraude max': temporal_stats['taux_fraude'].max()
    }
    
    # Sauvegarde des statistiques
    pd.Series(stats).to_csv(RESULTS_DIR / 'temporal_stats.csv')
    
    return stats

if __name__ == '__main__':
    stats = analyze_temporal_patterns()
    print("\nStatistiques temporelles :")
    for key, value in stats.items():
        print(f"{key}: {value:,.2f}")
