-- Création de la table transactions
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Clé primaire auto-incrémentée
    step INTEGER NOT NULL,  -- Jour de la simulation
    customer TEXT NOT NULL,  -- ID unique du client
    age TEXT NOT NULL,  -- Tranche d'âge du client (ex: '2', '3', 'U' pour inconnu)
    gender TEXT NOT NULL CHECK (gender IN ('F', 'M', 'E', 'U')),  -- Genre (F, M, Entreprise, Inconnu)
    zipcodeOri TEXT NOT NULL,  -- Code postal d'origine (tous 28007)
    merchant TEXT NOT NULL,  -- ID du commerçant
    zipMerchant TEXT NOT NULL,  -- Code postal du commerçant (tous 28007)
    category TEXT NOT NULL,  -- Catégorie de l'achat
    amount REAL NOT NULL CHECK (amount >= 0),  -- Montant de la transaction
    fraud INTEGER NOT NULL CHECK (fraud IN (0, 1))  -- 0 = normal, 1 = fraude
);

-- Indexation pour améliorer les performances
CREATE INDEX idx_transactions_step ON transactions(step);
CREATE INDEX idx_transactions_customer ON transactions(customer);
CREATE INDEX idx_transactions_merchant ON transactions(merchant);
CREATE INDEX idx_transactions_fraud ON transactions(fraud);
CREATE INDEX idx_transactions_category ON transactions(category);