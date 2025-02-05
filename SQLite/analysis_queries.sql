-- ============================================================================
-- STATISTIQUES GÉNÉRALES
-- ============================================================================

-- Statistiques globales sur les transactions
SELECT 
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS volume_total,
    ROUND(AVG(amount), 2) AS montant_moyen,
    ROUND(AVG(fraud) * 100, 2) AS taux_fraude_global,
    SUM(fraud) AS nombre_fraudes,
    COUNT(DISTINCT customer) AS clients_uniques,
    COUNT(DISTINCT merchant) AS commercants_uniques
FROM transactions;

-- ============================================================================
-- ANALYSE PAR GENRE
-- ============================================================================

-- Répartition des transactions et taux de fraude par genre
SELECT 
    gender,
    COUNT(*) AS nombre_transactions,
    ROUND(SUM(amount), 2) AS volume_total,
    ROUND(AVG(amount), 2) AS montant_moyen,
    SUM(fraud) AS nombre_fraudes,
    ROUND(AVG(fraud) * 100, 2) AS taux_fraude,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) AS pourcentage_transactions
FROM transactions
GROUP BY gender
ORDER BY nombre_transactions DESC;

-- ============================================================================
-- ANALYSE PAR CATÉGORIE
-- ============================================================================

-- Statistiques par catégorie
SELECT 
    category,
    COUNT(*) AS nombre_transactions,
    ROUND(SUM(amount), 2) AS volume_total,
    ROUND(AVG(amount), 2) AS montant_moyen,
    SUM(fraud) AS nombre_fraudes,
    ROUND(AVG(fraud) * 100, 2) AS taux_fraude,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) AS pourcentage_transactions
FROM transactions
GROUP BY category
ORDER BY volume_total DESC;

-- ============================================================================
-- ÉVOLUTION TEMPORELLE
-- ============================================================================

-- Évolution du nombre de transactions et du volume par step
SELECT 
    step,
    COUNT(*) AS nombre_transactions,
    ROUND(SUM(amount), 2) AS volume_total,
    ROUND(AVG(amount), 2) AS montant_moyen,
    SUM(fraud) AS nombre_fraudes,
    ROUND(AVG(fraud) * 100, 2) AS taux_fraude
FROM transactions
GROUP BY step
ORDER BY step;

-- ============================================================================
-- DISTRIBUTION DES MONTANTS
-- ============================================================================

-- Statistiques sur la distribution des montants
SELECT
    ROUND(MIN(amount), 2) AS montant_min,
    ROUND(MAX(amount), 2) AS montant_max,
    ROUND(AVG(amount), 2) AS moyenne,
    ROUND(AVG(CASE WHEN fraud = 1 THEN amount ELSE NULL END), 2) AS moyenne_fraudes,
    ROUND(AVG(CASE WHEN fraud = 0 THEN amount ELSE NULL END), 2) AS moyenne_non_fraudes,
    -- Approximation de la médiane en SQLite
    ROUND((
        SELECT amount
        FROM (
            SELECT amount, ROW_NUMBER() OVER (ORDER BY amount) as row_num,
                   COUNT(*) OVER () as total_rows
            FROM transactions
        )
        WHERE row_num IN ((total_rows + 1)/2, (total_rows + 2)/2)
        LIMIT 1
    ), 2) AS mediane
FROM transactions;

-- ============================================================================
-- PROFIL DES FRAUDES
-- ============================================================================

-- Répartition des fraudes par catégorie
WITH fraud_totals AS (
    SELECT SUM(fraud) as total_frauds
    FROM transactions
)
SELECT 
    category,
    SUM(fraud) AS nombre_fraudes,
    ROUND(AVG(fraud) * 100, 2) AS taux_fraude_categorie,
    ROUND(SUM(fraud) * 100.0 / (SELECT total_frauds FROM fraud_totals), 2) AS pourcentage_total_fraudes,
    ROUND(AVG(CASE WHEN fraud = 1 THEN amount ELSE NULL END), 2) AS montant_moyen_fraudes
FROM transactions
GROUP BY category
ORDER BY nombre_fraudes DESC;

-- Répartition des fraudes par genre
WITH fraud_totals AS (
    SELECT SUM(fraud) as total_frauds
    FROM transactions
)
SELECT 
    gender,
    SUM(fraud) AS nombre_fraudes,
    ROUND(AVG(fraud) * 100, 2) AS taux_fraude_genre,
    ROUND(SUM(fraud) * 100.0 / (SELECT total_frauds FROM fraud_totals), 2) AS pourcentage_total_fraudes,
    ROUND(AVG(CASE WHEN fraud = 1 THEN amount ELSE NULL END), 2) AS montant_moyen_fraudes
FROM transactions
GROUP BY gender
ORDER BY nombre_fraudes DESC;

-- ============================================================================
-- ANALYSE PAR TRANCHE DE MONTANT
-- ============================================================================

-- Distribution des transactions et fraudes par tranche de montant
WITH amount_ranges AS (
    SELECT 
        CASE 
            WHEN amount <= 10 THEN '0-10€'
            WHEN amount <= 20 THEN '10-20€'
            WHEN amount <= 50 THEN '20-50€'
            WHEN amount <= 100 THEN '50-100€'
            WHEN amount <= 200 THEN '100-200€'
            WHEN amount <= 500 THEN '200-500€'
            WHEN amount <= 1000 THEN '500-1000€'
            ELSE '> 1000€'
        END AS tranche_montant,
        fraud,
        amount
    FROM transactions
),
fraud_totals AS (
    SELECT SUM(fraud) as total_frauds
    FROM transactions
)
SELECT 
    tranche_montant,
    COUNT(*) AS nombre_transactions,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) AS pourcentage_transactions,
    SUM(fraud) AS nombre_fraudes,
    ROUND(AVG(fraud) * 100, 2) AS taux_fraude_tranche,
    ROUND(SUM(fraud) * 100.0 / (SELECT total_frauds FROM fraud_totals), 2) AS pourcentage_total_fraudes,
    ROUND(MIN(amount), 2) AS montant_min,
    ROUND(MAX(amount), 2) AS montant_max,
    ROUND(AVG(amount), 2) AS montant_moyen
FROM amount_ranges
GROUP BY tranche_montant
ORDER BY montant_min;
