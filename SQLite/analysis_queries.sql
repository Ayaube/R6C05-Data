-- 1. Statistiques générales sur le dataset
-- Nombre total de transactions
SELECT COUNT(*) AS total_transactions 
FROM transactions;

-- Nombre de clients uniques
SELECT COUNT(DISTINCT customer) AS total_customers 
FROM transactions;

-- Nombre de commerçants uniques
SELECT COUNT(DISTINCT merchant) AS total_merchants 
FROM transactions;

-- Nombre de transactions frauduleuses et taux de fraude
SELECT 
    COUNT(*) AS total_transactions,
    SUM(fraud) AS fraudulent_transactions,
    ROUND(AVG(fraud) * 100, 2) AS fraud_rate
FROM transactions;

-- 2. Analyse des montants
-- Statistiques descriptives des montants
SELECT 
    ROUND(AVG(amount), 2) AS montant_moyen,
    ROUND(MIN(amount), 2) AS montant_min,
    ROUND(MAX(amount), 2) AS montant_max,
    ROUND(SUM(amount), 2) AS montant_total
FROM transactions;

-- Distribution des montants par catégorie
SELECT 
    category,
    COUNT(*) AS nombre_transactions,
    ROUND(AVG(amount), 2) AS montant_moyen,
    ROUND(MIN(amount), 2) AS montant_min,
    ROUND(MAX(amount), 2) AS montant_max,
    ROUND(SUM(amount), 2) AS volume_total
FROM transactions
GROUP BY category
ORDER BY volume_total DESC;

-- 3. Analyse des fraudes
-- Taux de fraude par catégorie
SELECT 
    category,
    COUNT(*) AS total_transactions,
    SUM(fraud) AS fraudulent_transactions,
    ROUND(AVG(fraud) * 100, 2) AS fraud_rate,
    ROUND(SUM(CASE WHEN fraud = 1 THEN amount ELSE 0 END), 2) AS fraudulent_amount
FROM transactions
GROUP BY category
ORDER BY fraud_rate DESC;

-- Top 10 des commerçants avec le plus haut taux de fraude
SELECT 
    merchant,
    COUNT(*) AS total_transactions,
    SUM(fraud) AS fraudulent_transactions,
    ROUND(AVG(fraud) * 100, 2) AS fraud_rate,
    ROUND(SUM(amount), 2) AS volume_total
FROM transactions
GROUP BY merchant
HAVING total_transactions >= 100  -- Filtrer les commerçants avec peu de transactions
ORDER BY fraud_rate DESC
LIMIT 10;

-- 4. Analyse démographique
-- Répartition par genre
SELECT 
    gender,
    COUNT(*) AS total_transactions,
    ROUND(AVG(amount), 2) AS montant_moyen,
    ROUND(AVG(fraud) * 100, 2) AS fraud_rate
FROM transactions
GROUP BY gender;

-- Répartition par tranche d'âge
SELECT 
    CASE 
        WHEN age < 20 THEN '< 20'
        WHEN age BETWEEN 20 AND 30 THEN '20-30'
        WHEN age BETWEEN 31 AND 40 THEN '31-40'
        WHEN age BETWEEN 41 AND 50 THEN '41-50'
        WHEN age BETWEEN 51 AND 60 THEN '51-60'
        ELSE '> 60'
    END AS tranche_age,
    COUNT(*) AS total_transactions,
    ROUND(AVG(amount), 2) AS montant_moyen,
    ROUND(AVG(fraud) * 100, 2) AS fraud_rate
FROM transactions
GROUP BY tranche_age
ORDER BY tranche_age;

-- 5. Analyse temporelle
-- Nombre de transactions par jour
SELECT 
    step AS jour,
    COUNT(*) AS nombre_transactions,
    SUM(fraud) AS transactions_frauduleuses,
    ROUND(AVG(fraud) * 100, 2) AS taux_fraude,
    ROUND(SUM(amount), 2) AS volume_total
FROM transactions
GROUP BY step
ORDER BY step;

-- 6. Analyse des clients
-- Top 10 des clients par volume de transactions
SELECT 
    customer,
    COUNT(*) AS nombre_transactions,
    ROUND(SUM(amount), 2) AS volume_total,
    COUNT(DISTINCT merchant) AS nombre_commercants,
    COUNT(DISTINCT category) AS nombre_categories,
    SUM(fraud) AS transactions_frauduleuses
FROM transactions
GROUP BY customer
ORDER BY volume_total DESC
LIMIT 10;

-- 7. Analyse croisée
-- Matrice de corrélation catégorie-commerçant
SELECT 
    category,
    merchant,
    COUNT(*) AS nombre_transactions,
    ROUND(SUM(amount), 2) AS volume_total,
    ROUND(AVG(fraud) * 100, 2) AS taux_fraude
FROM transactions
GROUP BY category, merchant
HAVING nombre_transactions >= 50  -- Filtrer les combinaisons peu fréquentes
ORDER BY nombre_transactions DESC;

-- 8. Détection d'anomalies
-- Transactions avec des montants anormalement élevés
WITH category_stats AS (
    SELECT 
        category,
        COUNT(*) as n,
        AVG(amount) as mean_amount,
        AVG(amount * amount) as squared_mean
    FROM transactions
    GROUP BY category
),
stats AS (
    SELECT 
        category,
        mean_amount,
        SQRT(squared_mean - mean_amount * mean_amount) as std_amount
    FROM category_stats
)
SELECT 
    t.*,
    ROUND((t.amount - s.mean_amount) / CASE WHEN s.std_amount = 0 THEN 1 ELSE s.std_amount END, 2) AS zscore
FROM transactions t
JOIN stats s ON t.category = s.category
WHERE ABS((t.amount - s.mean_amount) / CASE WHEN s.std_amount = 0 THEN 1 ELSE s.std_amount END) > 3
ORDER BY ABS((t.amount - s.mean_amount) / CASE WHEN s.std_amount = 0 THEN 1 ELSE s.std_amount END) DESC;

-- 9. Patterns de fraude
-- Heures à risque (step = jour)
SELECT 
    step,
    COUNT(*) AS total_transactions,
    SUM(fraud) AS fraudulent_transactions,
    ROUND(AVG(fraud) * 100, 2) AS fraud_rate
FROM transactions
GROUP BY step
HAVING total_transactions >= 100
ORDER BY fraud_rate DESC;

-- Combinaisons à risque (catégorie-commerçant)
SELECT 
    category,
    merchant,
    COUNT(*) AS total_transactions,
    SUM(fraud) AS fraudulent_transactions,
    ROUND(AVG(fraud) * 100, 2) AS fraud_rate
FROM transactions
GROUP BY category, merchant
HAVING total_transactions >= 50
ORDER BY fraud_rate DESC
LIMIT 10;
