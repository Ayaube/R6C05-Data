"""
Analyse de la distribution des montants des transactions
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

def get_amount_data():
    """Récupère les données des montants"""
    query = """
    SELECT 
        amount,
        category,
        fraud
    FROM transactions
    ORDER BY amount;
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)

def analyze_amount_distribution():
    """Analyse et visualise la distribution des montants"""
    # Récupération des données
    data = get_amount_data()
    
    # Configuration de la figure
    plt.style.use('default')
    sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(2, 2)
    
    # 1. Distribution générale des montants (avec zoom sur les valeurs < 100€)
    ax1 = fig.add_subplot(gs[0, 0])
    sns.histplot(data=data[data['amount'] <= 100], 
                x='amount', bins=50, ax=ax1,
                color='lightcoral')
    ax1.set_title('Distribution des Montants (≤ 100€)\n'
                 f'{(data["amount"] <= 100).mean()*100:.1f}% des transactions')
    ax1.set_xlabel('Montant (€)')
    ax1.set_ylabel('Nombre de Transactions')
    
    # Ajouter la médiane
    median = data['amount'].median()
    if median <= 100:
        ax1.axvline(median, color='green', linestyle='--',
                   label=f'Médiane: {median:.2f}€')
        ax1.legend()
    
    # 2. Box plot par catégorie
    ax2 = fig.add_subplot(gs[0, 1])
    sns.boxplot(data=data, x='category', y='amount',
               ax=ax2, showfliers=False)
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
    ax2.set_title('Distribution des Montants par Catégorie\n(sans valeurs extrêmes)')
    ax2.set_xlabel('Catégorie')
    ax2.set_ylabel('Montant (€)')
    
    # 3. Distribution des montants élevés (> 100€)
    ax3 = fig.add_subplot(gs[1, 0])
    sns.histplot(data=data[data['amount'] > 100], 
                x='amount', bins=50, ax=ax3,
                color='lightblue')
    ax3.set_title('Distribution des Montants (> 100€)\n'
                 f'{(data["amount"] > 100).mean()*100:.1f}% des transactions')
    ax3.set_xlabel('Montant (€)')
    ax3.set_ylabel('Nombre de Transactions')
    
    # 4. Relation montant/fraude
    ax4 = fig.add_subplot(gs[1, 1])
    
    # Calculer le taux de fraude par tranche de montant
    bins = [0, 50, 100, 500, 1000, float('inf')]
    labels = ['0-50€', '50-100€', '100-500€', '500-1000€', '>1000€']
    data['amount_range'] = pd.cut(data['amount'], bins=bins, labels=labels)
    fraud_by_amount = data.groupby('amount_range')['fraud'].agg(['count', 'sum'])
    fraud_by_amount['rate'] = fraud_by_amount['sum'] / fraud_by_amount['count'] * 100
    
    sns.barplot(x=fraud_by_amount.index, y='rate', data=fraud_by_amount,
               ax=ax4, color='salmon')
    ax4.set_title('Taux de Fraude par Tranche de Montant')
    ax4.set_xlabel('Tranche de Montant')
    ax4.set_ylabel('Taux de Fraude (%)')
    
    # Ajouter le nombre de transactions sur chaque barre
    for i, v in enumerate(fraud_by_amount['count']):
        ax4.text(i, 0.1, f'n={v:,}', ha='center', va='bottom')
    
    # Statistiques descriptives
    stats = {
        'minimum': data['amount'].min(),
        'maximum': data['amount'].max(),
        'mediane': data['amount'].median(),
        'moyenne': data['amount'].mean(),
        'ecart_type': data['amount'].std(),
        'skewness': data['amount'].skew(),
        'max_categorie': data.loc[data['amount'].idxmax(), 'category'],
        'pct_inf_100': (data['amount'] <= 100).mean() * 100
    }
    
    # Ajouter un texte avec les statistiques principales
    fig.text(0.02, 0.02,
             f"Statistiques des Montants:\n"
             f"• Minimum: {stats['minimum']:.2f}€\n"
             f"• Maximum: {stats['maximum']:.2f}€ ({stats['max_categorie']})\n"
             f"• Médiane: {stats['mediane']:.2f}€\n"
             f"• Moyenne: {stats['moyenne']:.2f}€\n"
             f"• Écart-type: {stats['ecart_type']:.2f}€\n"
             f"• Asymétrie: {stats['skewness']:.2f}\n"
             f"• {stats['pct_inf_100']:.1f}% des transactions ≤ 100€",
             bbox=dict(facecolor='white', alpha=0.8),
             fontsize=10)
    
    # Ajustements finaux
    plt.suptitle('Analyse de la Distribution des Montants', fontsize=16, y=0.95)
    plt.tight_layout()
    
    # Sauvegarde
    plt.savefig(FIGURES_DIR / 'amount_distribution_analysis.png',
                dpi=300, bbox_inches='tight')
    plt.close()
    
    return stats

if __name__ == '__main__':
    stats = analyze_amount_distribution()
    print("\nStatistiques des montants :")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:,.2f}")
        else:
            print(f"{key}: {value}")
