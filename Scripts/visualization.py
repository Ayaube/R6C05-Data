"""
Module de visualisation pour l'analyse des données bancaires
"""

import logging
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

def setup_visualization_style():
    """
    Configure le style des visualisations
    """
    plt.style.use('seaborn')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['figure.dpi'] = 100

def plot_dataset_info(df: pd.DataFrame, save_dir: Path):
    """
    Visualise les informations générales du dataset
    """
    plt.figure(figsize=(10, 6))
    
    # Calculer les statistiques
    info = {
        'Total Transactions': len(df),
        'Clients Uniques': df['customer'].nunique(),
        'Commerçants': df['merchant'].nunique(),
        'Catégories': df['category'].nunique(),
        'Transactions Frauduleuses': df['fraud'].sum()
    }
    
    # Créer le graphique
    plt.bar(info.keys(), info.values())
    plt.xticks(rotation=45, ha='right')
    plt.title('Statistiques Générales du Dataset')
    plt.tight_layout()
    
    # Sauvegarder
    plt.savefig(save_dir / 'dataset_info.png')
    plt.close()

def plot_missing_values(df: pd.DataFrame, save_dir: Path):
    """
    Visualise les valeurs manquantes par colonne
    """
    plt.figure(figsize=(10, 6))
    
    # Calculer le pourcentage de valeurs manquantes
    missing = (df.isnull().sum() / len(df)) * 100
    
    # Créer le graphique
    plt.bar(missing.index, missing.values)
    plt.xticks(rotation=45, ha='right')
    plt.title('Pourcentage de Valeurs Manquantes par Colonne')
    plt.ylabel('Pourcentage (%)')
    plt.tight_layout()
    
    # Sauvegarder
    plt.savefig(save_dir / 'missing_values.png')
    plt.close()

def plot_amount_distribution(df: pd.DataFrame, save_dir: Path):
    """
    Visualise la distribution des montants
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Distribution globale
    sns.histplot(data=df, x='amount', bins=50, ax=ax1)
    ax1.set_title('Distribution des Montants de Transaction')
    ax1.set_xlabel('Montant (€)')
    
    # Boxplot par catégorie
    sns.boxplot(x='category', y='amount', data=df, ax=ax2)
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
    ax2.set_title('Distribution des Montants par Catégorie')
    
    plt.tight_layout()
    plt.savefig(save_dir / 'amount_distribution.png')
    plt.close()

def plot_category_analysis(df: pd.DataFrame, save_dir: Path):
    """
    Analyse détaillée par catégorie
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Nombre de transactions par catégorie
    category_counts = df['category'].value_counts()
    sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax1)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
    ax1.set_title('Nombre de Transactions par Catégorie')
    
    # Taux de fraude par catégorie
    fraud_by_category = df.groupby('category')['fraud'].agg(['count', 'sum'])
    fraud_by_category['rate'] = (fraud_by_category['sum'] / fraud_by_category['count']) * 100
    
    sns.barplot(x=fraud_by_category.index, y='rate', data=fraud_by_category, ax=ax2)
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
    ax2.set_title('Taux de Fraude par Catégorie (%)')
    
    plt.tight_layout()
    plt.savefig(save_dir / 'category_analysis.png')
    plt.close()

def plot_temporal_patterns(df: pd.DataFrame, save_dir: Path):
    """
    Analyse des patterns temporels
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Évolution du nombre de transactions
    daily_counts = df.groupby('step').size()
    rolling_mean = daily_counts.rolling(window=7).mean()
    
    ax1.plot(daily_counts.index, daily_counts.values, alpha=0.5, label='Transactions quotidiennes')
    ax1.plot(rolling_mean.index, rolling_mean.values, 'r', label='Moyenne mobile (7 jours)')
    ax1.set_title('Évolution Temporelle du Nombre de Transactions')
    ax1.set_xlabel('Jour')
    ax1.set_ylabel('Nombre de transactions')
    ax1.legend()
    
    # Taux de fraude quotidien
    daily_fraud = df.groupby('step')['fraud'].agg(['count', 'sum'])
    daily_fraud['rate'] = (daily_fraud['sum'] / daily_fraud['count']) * 100
    
    ax2.plot(daily_fraud.index, daily_fraud['rate'])
    ax2.set_title('Évolution du Taux de Fraude Quotidien')
    ax2.set_xlabel('Jour')
    ax2.set_ylabel('Taux de fraude (%)')
    
    plt.tight_layout()
    plt.savefig(save_dir / 'temporal_patterns.png')
    plt.close()

def plot_customer_analysis(df: pd.DataFrame, save_dir: Path):
    """
    Analyse des clients
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Distribution par âge
    sns.histplot(data=df, x='age', bins=30, ax=ax1)
    ax1.set_title('Distribution des Âges des Clients')
    
    # Distribution par genre
    gender_counts = df['gender'].value_counts()
    ax2.pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%')
    ax2.set_title('Répartition par Genre')
    
    # Montant moyen par âge
    age_amount = df.groupby('age')['amount'].mean()
    ax3.plot(age_amount.index, age_amount.values)
    ax3.set_title('Montant Moyen des Transactions par Âge')
    ax3.set_xlabel('Âge')
    ax3.set_ylabel('Montant moyen (€)')
    
    # Taux de fraude par démographie
    demo_fraud = df.groupby(['age', 'gender']).agg({
        'fraud': ['count', 'sum']
    })
    demo_fraud.columns = ['total', 'fraud']
    demo_fraud['rate'] = (demo_fraud['fraud'] / demo_fraud['total']) * 100
    demo_fraud = demo_fraud.reset_index()
    
    sns.scatterplot(data=demo_fraud, x='age', y='rate', hue='gender', 
                   size='total', sizes=(50, 400), alpha=0.6, ax=ax4)
    ax4.set_title('Taux de Fraude par Âge et Genre')
    ax4.set_xlabel('Âge')
    ax4.set_ylabel('Taux de fraude (%)')
    
    plt.tight_layout()
    plt.savefig(save_dir / 'customer_analysis.png')
    plt.close()

def plot_merchant_analysis(df: pd.DataFrame, save_dir: Path):
    """
    Analyse des commerçants
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Top 10 des commerçants par volume
    merchant_volume = df.groupby('merchant').agg({
        'amount': 'sum',
        'fraud': ['count', 'sum']
    })
    merchant_volume.columns = ['volume', 'transactions', 'fraudes']
    merchant_volume['taux_fraude'] = (merchant_volume['fraudes'] / merchant_volume['transactions']) * 100
    
    top_merchants = merchant_volume.nlargest(10, 'volume')
    sns.barplot(x=top_merchants.index, y='volume', data=top_merchants, ax=ax1)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
    ax1.set_title('Top 10 des Commerçants par Volume de Transactions')
    ax1.set_ylabel('Volume total (€)')
    
    # Taux de fraude par commerçant
    merchant_fraud = merchant_volume.nlargest(10, 'taux_fraude')
    sns.barplot(x=merchant_fraud.index, y='taux_fraude', data=merchant_fraud, ax=ax2)
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
    ax2.set_title('Top 10 des Commerçants par Taux de Fraude')
    ax2.set_ylabel('Taux de fraude (%)')
    
    plt.tight_layout()
    plt.savefig(save_dir / 'merchant_analysis.png')
    plt.close()

def generate_visualizations(df: pd.DataFrame, save_dir: Path):
    """
    Génère toutes les visualisations
    """
    logger.info("Génération des visualisations")
    
    # Créer le dossier de sauvegarde des figures
    figures_dir = save_dir / 'Figures'
    figures_dir.mkdir(exist_ok=True)
    
    # Configuration du style
    setup_visualization_style()
    
    # Générer toutes les visualisations
    plot_dataset_info(df, figures_dir)
    plot_missing_values(df, figures_dir)
    plot_amount_distribution(df, figures_dir)
    plot_category_analysis(df, figures_dir)
    plot_temporal_patterns(df, figures_dir)
    plot_customer_analysis(df, figures_dir)
    plot_merchant_analysis(df, figures_dir)
    
    logger.info(f"Visualisations sauvegardées dans {figures_dir}")
