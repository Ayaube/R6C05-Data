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

/*
==> Résultats :
+-------------------+--------------+---------------+------------------+--------------+----------------+-------------------+
| total_transactions | volume_total | montant_moyen | taux_fraude_global | nombre_fraudes | clients_uniques | commercants_uniques |
+-------------------+--------------+---------------+------------------+--------------+----------------+-------------------+
| 594643            | 22531103.73  | 37.89         | 1.21             | 7200         | 4112           | 50                |
+-------------------+--------------+---------------+------------------+--------------+----------------+-------------------+
*/


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

/*
==> Résultats :
+--------+-------------------+--------------+---------------+--------------+-------------+-------------------------+
| gender | nombre_transactions | volume_total | montant_moyen | nombre_fraudes | taux_fraude | pourcentage_transactions |
+--------+-------------------+--------------+---------------+--------------+-------------+-------------------------+
| F      | 324565            | 12727181.5   | 39.21         | 4758         | 1.47        | 54.58                   |
| M      | 268385            | 9744547.79   | 36.31         | 2435         | 0.91        | 45.13                   |
| E      | 1178              | 43147.34     | 36.63         | 7            | 0.59        | 0.2                     |
| U      | 515              | 16227.1      | 31.51         | 0            | 0           | 0.09                    |
+--------+-------------------+--------------+---------------+--------------+-------------+-------------------------+
*/

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

/*
==> Résultats :
+---------------------------+-------------------+--------------+---------------+--------------+-------------+-------------------------+
| category                  | nombre_transactions | volume_total | montant_moyen | nombre_fraudes | taux_fraude | pourcentage_transactions |
+---------------------------+-------------------+--------------+---------------+--------------+-------------+-------------------------+
| es_transportation         | 505119            | 13617092.46  | 26.96         | 0            | 0           | 84.94                   |
| es_health                 | 16133             | 2187979.51   | 135.62        | 1696         | 10.51       | 2.71                    |
| es_travel                 | 728               | 1638297.89   | 2250.41       | 578          | 79.4        | 0.12                    |
| es_wellnessandbeauty      | 15086             | 988302.28    | 65.51         | 718          | 4.76        | 2.54                    |
| es_food                   | 26254             | 973246.41    | 37.07         | 0            | 0           | 4.42                    |
| es_sportsandtoys          | 4002              | 863292.55    | 215.72        | 1982         | 49.53       | 0.67                    |
| es_fashion                | 6454              | 423812.51    | 65.67         | 116          | 1.8         | 1.09                    |
| es_hotelservices          | 1744              | 358591.25    | 205.61        | 548          | 31.42       | 0.29                    |
| es_home                   | 1986              | 329022.3     | 165.67        | 302          | 15.21       | 0.33                    |
| es_tech                   | 2370              | 286646.61    | 120.95        | 158          | 6.67        | 0.4                     |
| es_hyper                  | 6098              | 280327.63    | 45.97         | 280          | 4.59        | 1.03                    |
| es_barsandrestaurants     | 6373              | 276977.04    | 43.46         | 120          | 1.88        | 1.07                    |
| es_leisure                | 499               | 144166.74    | 288.91        | 474          | 94.99       | 0.08                    |
| es_otherservices          | 912               | 123923.95    | 135.88        | 228          | 25          | 0.15                    |
| es_contents               | 885               | 39424.6      | 44.55         | 0            | 0           | 0.15                    |
+---------------------------+-------------------+--------------+---------------+--------------+-------------+-------------------------+
*/

-- Répartition des volumes par catégorie :
SELECT
    category,
    ROUND(SUM(amount), 2) AS total_volume,
    ROUND((SUM(amount) * 100.0 / (SELECT SUM(amount) FROM transactions)), 2) AS volume_percentage
FROM transactions
GROUP BY category
ORDER BY volume_percentage DESC;

/*
==> Résultats :
+------------------------+---------------+------------------+
| category               | total_volume  | volume_percentage |
+------------------------+---------------+------------------+
| es_transportation      | 13617092.46   | 60.44            |
| es_health              | 2187979.51    | 9.71             |
| es_travel              | 1638297.89    | 7.27             |
| es_wellnessandbeauty   | 988302.28     | 4.39             |
| es_food                | 973246.41     | 4.32             |
| es_sportsandtoys       | 863292.55     | 3.83             |
| es_fashion             | 423812.51     | 1.88             |
| es_hotelservices       | 358591.25     | 1.59             |
| es_home                | 329022.3      | 1.46             |
| es_tech                | 286646.61     | 1.27             |
| es_hyper               | 280327.63     | 1.24             |
| es_barsandrestaurants  | 276977.04     | 1.23             |
| es_leisure             | 144166.74     | 0.64             |
| es_otherservices       | 123923.95     | 0.55             |
| es_contents            | 39424.6       | 0.17             |
+------------------------+---------------+------------------+
 */



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

/*
==> Résultats :
+------+-------------------+--------------+---------------+--------------+-------------+
| step | nombre_transactions | volume_total | montant_moyen | nombre_fraudes | taux_fraude |
+------+-------------------+--------------+---------------+--------------+-------------+
| 0    | 2430              | 92563.27     | 38.09         | 40           | 1.65        |
| 1    | 2424              | 101662.95    | 41.94         | 40           | 1.65        |
| 2    | 2462              | 102285.39    | 41.55         | 40           | 1.62        |
| 3    | 2499              | 107622.07    | 43.07         | 40           | 1.6         |
| 4    | 2532              | 104445.74    | 41.25         | 40           | 1.58        |
| 5    | 2525              | 96291.26     | 38.14         | 40           | 1.58        |
| 6    | 2580              | 121420.62    | 47.06         | 40           | 1.55        |
| 7    | 2539              | 116619.91    | 45.93         | 40           | 1.58        |
| 8    | 2575              | 103526.43    | 40.2          | 40           | 1.55        |
| 9    | 2638              | 96129.9      | 36.44         | 40           | 1.52        |
| 10   | 2622              | 99146.41     | 37.81         | 40           | 1.53        |
| 11   | 2636              | 95654.28     | 36.29         | 40           | 1.52        |
| 12   | 2671              | 95403.23     | 35.72         | 40           | 1.5         |
| 13   | 2682              | 115912.41    | 43.22         | 40           | 1.49        |
| 14   | 2723              | 95916.94     | 35.22         | 40           | 1.47        |
| 15   | 2699              | 100090.55    | 37.08         | 40           | 1.48        |
| 16   | 2688              | 110208       | 41            | 40           | 1.49        |
| 17   | 2709              | 104622.39    | 38.62         | 40           | 1.48        |
| 18   | 2758              | 112075.7     | 40.64         | 40           | 1.45        |
| 19   | 2734              | 103430.24    | 37.83         | 40           | 1.46        |
| 20   | 2761              | 111738.66    | 40.47         | 40           | 1.45        |
| 21   | 2789              | 113938.24    | 40.85         | 40           | 1.43        |
| 22   | 2797              | 105096.45    | 37.57         | 40           | 1.43        |
| 23   | 2797              | 116036.17    | 41.49         | 40           | 1.43        |
| 24   | 2806              | 100768.64    | 35.91         | 40           | 1.43        |
| 25   | 2859              | 107896.45    | 37.74         | 40           | 1.4         |
| 26   | 2886              | 109683.33    | 38.01         | 40           | 1.39        |
| 27   | 2897              | 120338.08    | 41.54         | 40           | 1.38        |
| 28   | 2878              | 117165.31    | 40.71         | 40           | 1.39        |
| 29   | 2883              | 121816.43    | 42.25         | 40           | 1.39        |
| 30   | 2895              | 108101.71    | 37.34         | 40           | 1.38        |
+------+-------------------+--------------+---------------+--------------+-------------+
Le tableau obtenu contient 180 tuples, nous avons décidé de ne pas tout présenter ici.
*/

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

/*
==> Résultats :
+-------------+------------+---------+----------------+-------------------+---------+
| montant_min | montant_max | moyenne | moyenne_fraudes | moyenne_non_fraudes | mediane |
+-------------+------------+---------+----------------+-------------------+---------+
| 0           | 8329.96    | 37.89   | 530.93         | 31.85             | 26.9    |
+-------------+------------+---------+----------------+-------------------+---------+
*/


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

/*
==> Résultats :
+------------------------+---------------+--------------------+--------------------------+----------------------+
| category               | nombre_fraudes | taux_fraude_categorie | pourcentage_total_fraudes | montant_moyen_fraudes |
+------------------------+---------------+--------------------+--------------------------+----------------------+
| es_sportsandtoys       | 1982          | 49.53              | 27.53                    | 345.37               |
| es_health              | 1696          | 10.51              | 23.56                    | 407.03               |
| es_wellnessandbeauty   | 718           | 4.76               | 9.97                     | 229.42               |
| es_travel              | 578           | 79.4               | 8.03                     | 2660.8               |
| es_hotelservices       | 548           | 31.42              | 7.61                     | 421.82               |
| es_leisure             | 474           | 94.99              | 6.58                     | 300.29               |
| es_home                | 302           | 15.21              | 4.19                     | 457.48               |
| es_hyper               | 280           | 4.59               | 3.89                     | 169.26               |
| es_otherservices       | 228           | 25                 | 3.17                     | 316.47               |
| es_tech                | 158           | 6.67               | 2.19                     | 415.27               |
| es_barsandrestaurants  | 120           | 1.88               | 1.67                     | 164.09               |
| es_fashion             | 116           | 1.8                | 1.61                     | 247.01               |
| es_contents            | 0             | 0                  | 0                        | null                 |
| es_food                | 0             | 0                  | 0                        | null                 |
| es_transportation      | 0             | 0                  | 0                        | null                 |
+------------------------+---------------+--------------------+--------------------------+----------------------+
*/


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

/*
==> Résultats :
+--------+---------------+------------------+--------------------------+----------------------+
| gender | nombre_fraudes | taux_fraude_genre | pourcentage_total_fraudes | montant_moyen_fraudes |
+--------+---------------+------------------+--------------------------+----------------------+
| F      | 4758          | 1.47             | 66.08                    | 526.18               |
| M      | 2435          | 0.91             | 33.82                    | 540.37               |
| E      | 7             | 0.59             | 0.1                      | 473.46               |
| U      | 0             | 0                | 0                        | null                 |
+--------+---------------+------------------+--------------------------+----------------------+
*/

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

/*
==> Résultats :
+---------------+------------------+--------------------------+---------------+--------------------+--------------------------+-------------+-------------+--------------+
| tranche_montant | nombre_transactions | pourcentage_transactions | nombre_fraudes | taux_fraude_tranche | pourcentage_total_fraudes | montant_min | montant_max | montant_moyen |
+---------------+------------------+--------------------------+---------------+--------------------+--------------------------+-------------+-------------+--------------+
| 0-10€         | 107469           | 18.07                    | 115           | 0.11               | 1.6                      | 0           | 10          | 5.03         |
| 10-20€        | 112090           | 18.85                    | 109           | 0.1                | 1.51                     | 10.01       | 20          | 15.04        |
| 20-50€        | 274357           | 46.14                    | 365           | 0.13               | 5.07                     | 20.01       | 50          | 33.24        |
| 50-100€       | 80172            | 13.48                    | 550           | 0.69               | 7.64                     | 50.01       | 100         | 63.23        |
| 100-200€      | 12911            | 2.17                     | 1106          | 8.57               | 15.36                    | 100.01      | 199.98      | 137.57       |
| 200-500€      | 5480             | 0.92                     | 2879          | 52.54              | 39.99                    | 200.05      | 499.84      | 294.01       |
| 500-1000€     | 1526             | 0.26                     | 1469          | 96.26              | 20.4                     | 500.13      | 996.38      | 679.15       |
| > 1000€       | 638              | 0.11                     | 607           | 95.14              | 8.43                     | 1000.42     | 8329.96     | 2653.36      |
+---------------+------------------+--------------------------+---------------+--------------------+--------------------------+-------------+-------------+--------------+

*/
