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
    SELECT 
        category,
        COUNT(*) AS transactions,
        ROUND(SUM(amount), 2) AS volume,
        ROUND(AVG(amount), 2) AS avg_amount,
        ROUND(AVG(fraud) * 100, 2) AS fraud_rate
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
    
    # 3. Taux de fraude par catégorie (milieu centre)
    ax_fraud = fig.add_subplot(gs[1, 1])
    top_fraud = category_kpis.nlargest(5, 'fraud_rate')
    sns.barplot(data=top_fraud, y='category', x='fraud_rate', ax=ax_fraud)
    ax_fraud.set_title('Top 5 Catégories par Taux de Fraude (%)')
    
    # 4. Distribution par genre (milieu droite)
    ax_gender = fig.add_subplot(gs[1, 2])
    gender_kpis['gender'] = gender_kpis['gender'].replace({
        'F': 'Femme', 'M': 'Homme', 'E': 'Entreprise', 'U': 'Inconnu'
    })
    ax_gender.pie(gender_kpis['transactions'], labels=gender_kpis['gender'],
                 autopct='%1.1f%%')
    ax_gender.set_title('Répartition des Transactions par Genre')
    
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
