"""
Analyse des cycles dans les transactions
"""

import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.signal import find_peaks
import seaborn as sns

# Configuration
DB_PATH = Path(__file__).parent.parent / 'SQLite' / 'bankdata.db'
RESULTS_DIR = Path(__file__).parent.parent / 'Results'
FIGURES_DIR = RESULTS_DIR / 'Figures'
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def get_daily_transactions():
    """Récupère le nombre de transactions par jour"""
    query = """
    SELECT 
        step,
        COUNT(*) as nb_transactions,
        SUM(fraud) as nb_fraudes,
        ROUND(AVG(amount), 2) as montant_moyen
    FROM transactions
    GROUP BY step
    ORDER BY step;
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)

def analyze_cycles():
    """Analyse et visualise les cycles dans les transactions"""
    # Récupération des données
    daily_data = get_daily_transactions()
    
    # Configuration de la figure
    plt.style.use('default')
    sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(2, 2)
    
    # 1. Série temporelle avec pics détectés
    ax1 = fig.add_subplot(gs[0, :])
    x = daily_data['nb_transactions'].values
    
    # Détection des pics
    peaks, _ = find_peaks(x, distance=5, prominence=100)
    
    # Tracer la série et les pics
    ax1.plot(daily_data['step'], x, label='Transactions')
    ax1.plot(daily_data['step'].iloc[peaks], x[peaks], "x", color='red',
             label='Pics détectés', markersize=10)
    
    # Calculer et afficher la distance moyenne entre les pics
    peak_distances = np.diff(peaks)
    mean_distance = np.mean(peak_distances)
    std_distance = np.std(peak_distances)
    
    ax1.set_title(f'Série Temporelle avec Pics\n'
                 f'Distance moyenne entre pics: {mean_distance:.1f} ± {std_distance:.1f} jours')
    ax1.set_xlabel('Jour')
    ax1.set_ylabel('Nombre de Transactions')
    ax1.legend()
    
    # 2. Autocorrélation
    ax2 = fig.add_subplot(gs[1, 0])
    pd.plotting.autocorrelation_plot(daily_data['nb_transactions'], ax=ax2)
    ax2.set_title('Autocorrélation des Transactions')
    ax2.set_xlim(0, 30)  # Focus sur les 30 premiers lags
    
    # 3. Analyse par jour de la semaine
    ax3 = fig.add_subplot(gs[1, 1])
    daily_data['day_of_week'] = daily_data['step'] % 7
    day_mapping = {
        0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi',
        4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'
    }
    daily_data['day_name'] = daily_data['day_of_week'].map(day_mapping)
    
    # Calculer les statistiques par jour
    weekly_stats = daily_data.groupby('day_name')['nb_transactions'].agg([
        'mean', 'std'
    ]).reset_index()
    weekly_stats = weekly_stats.sort_values('mean', ascending=False)
    
    # Tracer le graphique avec barres d'erreur
    ax3.bar(range(7), weekly_stats['mean'], yerr=weekly_stats['std'],
            capsize=5, alpha=0.8)
    ax3.set_xticks(range(7))
    ax3.set_xticklabels(weekly_stats['day_name'], rotation=45)
    ax3.set_title('Moyenne des Transactions par Jour de la Semaine')
    ax3.set_ylabel('Nombre moyen de transactions')
    
    # Ajustements finaux
    plt.suptitle('Analyse des Cycles dans les Transactions', fontsize=16, y=0.95)
    plt.tight_layout()
    
    # Sauvegarde
    plt.savefig(FIGURES_DIR / 'cycle_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Calcul des statistiques sur les cycles
    stats = {
        'distance_moyenne_pics': mean_distance,
        'ecart_type_distance': std_distance,
        'jour_plus_actif': weekly_stats.iloc[0]['day_name'],
        'jour_moins_actif': weekly_stats.iloc[-1]['day_name'],
        'variation_hebdomadaire': (weekly_stats['mean'].max() - weekly_stats['mean'].min()) / weekly_stats['mean'].min() * 100
    }
    
    # Sauvegarde des statistiques
    pd.Series(stats).to_csv(RESULTS_DIR / 'cycle_stats.csv')
    
    return stats

if __name__ == '__main__':
    stats = analyze_cycles()
    print("\nStatistiques des cycles :")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
