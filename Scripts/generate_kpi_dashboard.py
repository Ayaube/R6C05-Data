"""
Génération d'un dashboard des KPIs principaux
"""

import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
DB_PATH = Path(__file__).parent.parent / 'SQLite' / 'bankdata.db'
RESULTS_DIR = Path(__file__).parent.parent / 'Results'
FIGURES_DIR = RESULTS_DIR / 'Figures'
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Configuration du style
plt.style.use('default')
sns.set_theme(style="whitegrid")
sns.set_palette("husl")

def get_general_kpis():
    """Récupère les KPIs généraux"""
    query = """
    SELECT 
        COUNT(*) AS total_transactions,
        COUNT(DISTINCT customer) AS total_customers,
        COUNT(DISTINCT merchant) AS total_merchants,
        SUM(fraud) AS fraudulent_transactions,
        ROUND(AVG(fraud) * 100, 2) AS fraud_rate,
        ROUND(SUM(amount), 2) AS total_amount,
        ROUND(AVG(amount), 2) AS avg_amount
    FROM transactions;
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn).iloc[0]

def get_category_kpis():
    """Récupère les KPIs par catégorie"""
    query = """
    WITH fraud_totals AS (
        SELECT SUM(fraud) as total_frauds
        FROM transactions
    )
    SELECT 
        category,
        COUNT(*) AS transactions,
        ROUND(SUM(amount), 2) AS volume,
        ROUND(AVG(amount), 2) AS avg_amount,
        SUM(fraud) as fraud_count,
        ROUND(AVG(fraud) * 100, 2) AS fraud_rate,
        ROUND(SUM(fraud) * 100.0 / (SELECT total_frauds FROM fraud_totals), 2) AS fraud_distribution
    FROM transactions
    GROUP BY category
    ORDER BY volume DESC;
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)

def get_gender_kpis():
    """Récupère les KPIs par genre"""
    query = """
    SELECT 
        gender,
        COUNT(*) AS transactions,
        ROUND(SUM(amount), 2) AS volume,
        ROUND(AVG(fraud) * 100, 2) AS fraud_rate
    FROM transactions
    GROUP BY gender;
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)

def create_kpi_dashboard():
    """Crée un dashboard avec les KPIs principaux"""
    # Récupération des données
    general_kpis = get_general_kpis()
    category_kpis = get_category_kpis()
    gender_kpis = get_gender_kpis()
    
    # Création de la figure
    fig = plt.figure(figsize=(20, 12))
    
    # Layout
    gs = fig.add_gridspec(3, 3)
    
    # 1. KPIs généraux (en haut)
    ax_general = fig.add_subplot(gs[0, :])
    ax_general.axis('off')
    kpi_text = (
        f"STATISTIQUES GÉNÉRALES\n\n"
        f"Transactions: {general_kpis['total_transactions']:,}\n"
        f"Volume total: {general_kpis['total_amount']:,.2f}€\n"
        f"Clients uniques: {general_kpis['total_customers']:,}\n"
        f"Commerçants: {general_kpis['total_merchants']:,}\n"
        f"Fraudes: {general_kpis['fraudulent_transactions']:,} ({general_kpis['fraud_rate']}%)\n"
        f"Montant moyen: {general_kpis['avg_amount']:.2f}€"
    )
    ax_general.text(0.5, 0.5, kpi_text, 
                   ha='center', va='center',
                   fontsize=12, fontweight='bold',
                   bbox=dict(facecolor='white', alpha=0.8))
    
    # 2. Top 5 catégories par volume (milieu gauche)
    ax_categories = fig.add_subplot(gs[1, 0])
    top_categories = category_kpis.head()
    sns.barplot(data=top_categories, y='category', x='volume', ax=ax_categories)
    ax_categories.set_title('Top 5 Catégories par Volume (€)')
    
    # 3. Analyse des fraudes par catégorie (milieu centre)
    ax_fraud = fig.add_subplot(gs[1, 1])
    
    # Sélectionner les 6 catégories avec le plus haut taux de fraude
    top_fraud = category_kpis.nlargest(6, 'fraud_rate')
    
    # Créer un graphique à barres empilées
    x = range(len(top_fraud))
    width = 0.35
    
    # Première série de barres : Taux de fraude dans la catégorie
    bars1 = ax_fraud.barh(x, top_fraud['fraud_rate'], width, 
                         label='Taux de fraude dans la catégorie',
                         color='lightcoral')
    
    # Deuxième série de barres : Distribution des fraudes
    bars2 = ax_fraud.barh([i + width for i in x], top_fraud['fraud_distribution'], width,
                         label='% du total des fraudes',
                         color='lightblue')
    
    # Ajouter les valeurs sur les barres
    def add_labels(bars):
        for bar in bars:
            width = bar.get_width()
            ax_fraud.text(width, bar.get_y() + bar.get_height()/2,
                         f'{width:.1f}%', ha='left', va='center')
    
    add_labels(bars1)
    add_labels(bars2)
    
    # Personnaliser l'apparence
    ax_fraud.set_yticks([i + width/2 for i in x])
    ax_fraud.set_yticklabels(top_fraud['category'])
    ax_fraud.set_title('Top 6 Catégories par Taux de Fraude')
    ax_fraud.set_xlabel('Pourcentage (%)')
    ax_fraud.legend()
    
    # 4. Distribution par genre (milieu droite)
    ax_gender = fig.add_subplot(gs[1, 2])
    gender_kpis['gender'] = gender_kpis['gender'].replace({
        'F': 'Femme', 'M': 'Homme', 'E': 'Entreprise', 'U': 'Inconnu'
    })
    
    # Trier par volume décroissant pour une meilleure lisibilité
    gender_kpis = gender_kpis.sort_values('transactions', ascending=False)
    
    # Utiliser un graphique en barres au lieu d'un camembert
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99']
    bars = ax_gender.bar(range(len(gender_kpis)), gender_kpis['transactions'], 
                        color=colors)
    
    # Ajouter les pourcentages sur les barres
    total = gender_kpis['transactions'].sum()
    for bar in bars:
        height = bar.get_height()
        percentage = (height/total) * 100
        ax_gender.text(bar.get_x() + bar.get_width()/2., height,
                      f'{percentage:.1f}%',
                      ha='center', va='bottom')
    
    # Personnaliser l'apparence
    ax_gender.set_xticks(range(len(gender_kpis)))
    ax_gender.set_xticklabels(gender_kpis['gender'], rotation=45)
    ax_gender.set_title('Répartition des Transactions par Genre')
    ax_gender.set_ylabel('Nombre de Transactions')
    
    # 5. Montant moyen par catégorie (bas gauche)
    ax_amount = fig.add_subplot(gs[2, 0])
    top_amount = category_kpis.nlargest(5, 'avg_amount')
    sns.barplot(data=top_amount, y='category', x='avg_amount', ax=ax_amount)
    ax_amount.set_title('Top 5 Catégories par Montant Moyen (€)')
    
    # 6. Volume par genre (bas centre)
    ax_gender_volume = fig.add_subplot(gs[2, 1])
    sns.barplot(data=gender_kpis, x='gender', y='volume', ax=ax_gender_volume)
    ax_gender_volume.set_title('Volume de Transactions par Genre (€)')
    ax_gender_volume.tick_params(axis='x', rotation=45)
    
    # 7. Taux de fraude par genre (bas droite)
    ax_gender_fraud = fig.add_subplot(gs[2, 2])
    sns.barplot(data=gender_kpis, x='gender', y='fraud_rate', ax=ax_gender_fraud)
    ax_gender_fraud.set_title('Taux de Fraude par Genre (%)')
    ax_gender_fraud.tick_params(axis='x', rotation=45)
    
    # Ajustements finaux
    plt.suptitle('Dashboard des KPIs - Analyse des Transactions Bancaires', 
                fontsize=16, y=0.95)
    plt.tight_layout()
    
    # Sauvegarde
    plt.savefig(FIGURES_DIR / 'kpi_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    create_kpi_dashboard()
