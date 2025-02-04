"""
Configuration globale pour l'analyse des données bancaires
"""

import os
from pathlib import Path

# Chemins des données
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = ROOT_DIR / 'Dataset'
RESULTS_DIR = ROOT_DIR / 'Results'
FIGURES_DIR = RESULTS_DIR / 'Figures'

# Création des dossiers nécessaires
RESULTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

# Fichiers de données
DATA_FILE = DATA_DIR / 'big.csv'
DATA_FILE_SMALL = DATA_DIR / 'small.csv'

# Configuration des graphiques
FIGURE_SIZE = (12, 8)
STYLE = 'seaborn'
DPI = 300

# Paramètres d'analyse
AMOUNT_BINS = [0, 100, 500, 1000, 2000, 5000, float('inf')]
AMOUNT_LABELS = ['0-100', '100-500', '500-1000', '1000-2000', '2000-5000', '>5000']

# Colonnes attendues dans le dataset
EXPECTED_COLUMNS = [
    'step', 'customer', 'age', 'gender', 'merchant', 'category',
    'amount', 'fraud'
]
