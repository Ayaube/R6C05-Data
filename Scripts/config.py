"""
Configuration globale pour l'analyse des données bancaires
"""

import os
import logging
from pathlib import Path

# Chemins des données
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS_DIR = ROOT_DIR / 'Results'
FIGURES_DIR = RESULTS_DIR / 'Figures'
SQLITE_DIR = ROOT_DIR / 'SQLite'

# Création des dossiers nécessaires
RESULTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)
SQLITE_DIR.mkdir(exist_ok=True)

# Base de données SQLite
DB_PATH = SQLITE_DIR / 'bankdata.db'

# Configuration du logging
LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

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
