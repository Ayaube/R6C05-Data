"""
Analyse automatique des fichiers CSV générés par les requêtes SQL
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def analyze_csv_file(file_path: Path) -> dict:
    """Analyse un fichier CSV et retourne un dictionnaire avec les informations pertinentes"""
    df = pd.read_csv(file_path)
    
    # Informations de base
    info = {
        'nom_fichier': file_path.name,
        'nombre_lignes': len(df),
        'nombre_colonnes': len(df.columns),
        'colonnes': list(df.columns)
    }
    
    # Analyse spécifique selon le fichier
    if file_path.name == 'age_distribution.csv':
        info['description'] = "Distribution des âges des clients"
        info['statistiques'] = {
            'age_moyen': df['montant_moyen'].mean(),
            'tranche_age_principale': df.iloc[df['total_transactions'].idxmax()]['tranche_age'],
            'transactions_max': df['total_transactions'].max()
        }
        
    elif file_path.name == 'amount_by_category.csv':
        info['description'] = "Montants des transactions par catégorie"
        info['statistiques'] = {
            'categorie_plus_importante': df.iloc[df['volume_total'].idxmax()]['category'],
            'montant_max': df['volume_total'].max(),
            'montant_moyen': df['montant_moyen'].mean()
        }
        
    elif file_path.name == 'amount_statistics.csv':
        info['description'] = "Statistiques générales sur les montants"
        info['statistiques'] = df.to_dict('records')[0]
        
    elif file_path.name == 'category_merchant_correlation.csv':
        info['description'] = "Corrélation entre catégories et marchands"
        info['statistiques'] = {
            'nb_combinaisons': len(df),
            'volume_max': df['volume_total'].max(),
            'paire_plus_frequente': f"{df.iloc[df['nombre_transactions'].idxmax()]['category']} - {df.iloc[df['nombre_transactions'].idxmax()]['merchant']}"
        }
        
    elif file_path.name == 'daily_transactions.csv':
        info['description'] = "Nombre de transactions par jour"
        info['statistiques'] = {
            'jour_plus_actif': df.iloc[df['nombre_transactions'].idxmax()]['jour'],
            'max_transactions': df['nombre_transactions'].max(),
            'moyenne_transactions': df['nombre_transactions'].mean()
        }
        
    elif file_path.name == 'fraud_by_category.csv':
        info['description'] = "Analyse des fraudes par catégorie"
        info['statistiques'] = {
            'categorie_plus_risquee': df.iloc[df['fraud_rate'].idxmax()]['category'],
            'taux_fraude_max': df['fraud_rate'].max(),
            'montant_fraudes_total': df['fraudulent_amount'].sum()
        }
        
    elif file_path.name == 'fraud_by_time.csv':
        info['description'] = "Évolution temporelle des fraudes"
        info['statistiques'] = {
            'jour_plus_risque': df.iloc[df['fraud_rate'].idxmax()]['step'],
            'taux_fraude_max': df['fraud_rate'].max(),
            'nb_fraudes_total': df['fraudulent_transactions'].sum()
        }
        
    elif file_path.name == 'fraud_statistics.csv':
        info['description'] = "Statistiques générales sur les fraudes"
        info['statistiques'] = df.to_dict('records')[0]
        
    elif file_path.name == 'gender_distribution.csv':
        info['description'] = "Distribution des genres des clients"
        info['statistiques'] = {
            'transactions_par_genre': df.set_index('gender')['total_transactions'].to_dict(),
            'montant_moyen_max': df['montant_moyen'].max(),
            'taux_fraude_moyen': df['fraud_rate'].mean()
        }
        
    elif file_path.name == 'high_risk_combinations.csv':
        info['description'] = "Combinaisons à haut risque de fraude"
        info['statistiques'] = {
            'nb_combinaisons': len(df),
            'taux_fraude_max': df['fraud_rate'].max(),
            'combinaison_plus_risquee': f"{df.iloc[0]['category']} - {df.iloc[0]['merchant']}"
        }
        
    elif file_path.name == 'top_customers.csv':
        info['description'] = "Top des clients par volume de transactions"
        info['statistiques'] = {
            'client_plus_actif': df.iloc[0]['customer'],
            'nb_transactions_max': df['nombre_transactions'].max(),
            'montant_max': df['volume_total'].max()
        }
        
    elif file_path.name == 'top_fraud_merchants.csv':
        info['description'] = "Top des marchands avec le plus de fraudes"
        info['statistiques'] = {
            'marchand_plus_risque': df.iloc[0]['merchant'],
            'taux_fraude_max': df['fraud_rate'].max(),
            'nb_fraudes_max': df['fraudulent_transactions'].max()
        }
        
    else:
        info['description'] = "Fichier de données générales"
        if len(df) == 1:  # Pour les fichiers de totaux
            info['statistiques'] = df.to_dict('records')[0]
        else:
            info['statistiques'] = {
                'nombre_entrees': len(df)
            }
    
    return info

def main():
    """Fonction principale qui analyse tous les fichiers CSV"""
    # Chemin vers le dossier Scripts
    script_dir = Path(__file__).parent
    
    # Liste tous les fichiers CSV
    csv_files = list(script_dir.glob('*.csv'))
    
    # Analyse chaque fichier
    results = {}
    for file_path in csv_files:
        try:
            results[file_path.name] = analyze_csv_file(file_path)
        except Exception as e:
            print(f"Erreur lors de l'analyse de {file_path.name}: {str(e)}")
    
    # Affiche les résultats
    for filename, info in results.items():
        print(f"\n{'='*80}")
        print(f"Fichier: {filename}")
        print(f"Description: {info['description']}")
        print(f"Nombre de lignes: {info['nombre_lignes']}")
        print(f"Colonnes: {', '.join(info['colonnes'])}")
        print("\nStatistiques principales:")
        for key, value in info['statistiques'].items():
            if isinstance(value, float):
                print(f"• {key}: {value:,.2f}")
            elif isinstance(value, dict):
                print(f"• {key}:")
                for k, v in value.items():
                    print(f"  - {k}: {v:,}")
            else:
                print(f"• {key}: {value}")

if __name__ == '__main__':
    main()