-- ============================================================================
-- 04_olap_queries.sql
-- Project: Movie Data Warehouse & Data Mining
-- Description: OLAP analytical queries answering Research Question Q3:
--              "Which genres are experiencing the fastest growth in recent quarters?"
--              Demonstrates ROLLUP, CUBE, window function LAG() for QoQ growth,
--              ranking, Drill-Down, Roll-Up, Slice, Dice, and Pivot.
-- ============================================================================

USE MovieDW;
GO

-- ============================================================================
-- 1. CORE Q3 QUERY: QUARTER-OVER-QUARTER (QoQ) GROWTH BY GENRE
-- Calculates total views, previous quarter views using LAG(), QoQ growth %,
-- and ranks the fastest growing genres in each quarter.
-- ============================================================================
PRINT '=== 1. QoQ GENRE GROWTH ANALYSIS (WINDOW FUNCTION LAG) ===';

WITH QuarterlyGenreStats AS (
    SELECT 
        d.[year],
        d.[quarter],
        g.genre_name,
        COUNT(f.rating_id) AS total_views,
        ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS avg_rating,
        ROUND(SUM(CAST(f.watch_minutes AS BIGINT)) / 60.0, 1) AS total_watch_hours
    FROM dw.FactRating f
    JOIN dw.DimDate d ON d.date_key = f.date_key
    JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
    JOIN dw.DimGenre g ON g.genre_key = b.genre_key
    GROUP BY d.[year], d.[quarter], g.genre_name
),
QoQCalculation AS (
    SELECT 
        [year],
        [quarter],
        genre_name,
        total_views,
        avg_rating,
        total_watch_hours,
        LAG(total_views, 1) OVER (
            PARTITION BY genre_name 
            ORDER BY [year], [quarter]
        ) AS prev_quarter_views
    FROM QuarterlyGenreStats
)
SELECT 
    [year],
    [quarter],
    genre_name,
    total_views,
    ISNULL(prev_quarter_views, 0) AS prev_quarter_views,
    CASE 
        WHEN prev_quarter_views IS NULL OR prev_quarter_views = 0 THEN NULL
        ELSE ROUND(((CAST(total_views AS FLOAT) - prev_quarter_views) / prev_quarter_views) * 100.0, 2)
    END AS qoq_growth_pct,
    avg_rating,
    total_watch_hours,
    DENSE_RANK() OVER (
        PARTITION BY [year], [quarter] 
        ORDER BY 
            CASE 
                WHEN prev_quarter_views IS NULL OR prev_quarter_views = 0 THEN -999999
                ELSE ((CAST(total_views AS FLOAT) - prev_quarter_views) / prev_quarter_views)
            END DESC
    ) AS growth_rank_in_quarter
FROM QoQCalculation
ORDER BY [year] DESC, [quarter] DESC, growth_rank_in_quarter ASC;
GO

-- ============================================================================
-- 2. OLAP OPERATION: ROLLUP BY (YEAR, QUARTER, GENRE)
-- Generates hierarchical aggregations:
-- - Genre level within Quarter
-- - Quarter sub-total
-- - Year sub-total
-- - Grand Total across all time
-- ============================================================================
PRINT '=== 2. OLAP ROLLUP (YEAR -> QUARTER -> GENRE) ===';

SELECT 
    CASE WHEN GROUPING(d.[year]) = 1 THEN 'All Years' ELSE CAST(d.[year] AS VARCHAR) END AS [year],
    CASE WHEN GROUPING(d.[quarter]) = 1 THEN 'All Quarters' ELSE 'Q' + CAST(d.[quarter] AS VARCHAR) END AS [quarter],
    CASE WHEN GROUPING(g.genre_name) = 1 THEN 'All Genres (Subtotal)' ELSE g.genre_name END AS genre_name,
    COUNT(f.rating_id) AS total_views,
    ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS avg_rating,
    ROUND(SUM(CAST(f.watch_minutes AS BIGINT)) / 60.0, 1) AS total_watch_hours
FROM dw.FactRating f
JOIN dw.DimDate d ON d.date_key = f.date_key
JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
JOIN dw.DimGenre g ON g.genre_key = b.genre_key
GROUP BY ROLLUP (d.[year], d.[quarter], g.genre_name)
ORDER BY d.[year], d.[quarter], g.genre_name;
GO

-- ============================================================================
-- 3. OLAP OPERATION: CUBE BY (GENDER, AGE GROUP, GENRE)
-- Computes all $2^3 = 8$ cross-dimensional combinations across user demographics and genre
-- ============================================================================
PRINT '=== 3. OLAP CUBE (GENDER x AGE GROUP x GENRE) ===';

SELECT 
    CASE WHEN GROUPING(u.gender) = 1 THEN 'All Genders' ELSE u.gender END AS gender,
    CASE WHEN GROUPING(u.age_group) = 1 THEN 'All Age Groups' ELSE u.age_group END AS age_group,
    CASE WHEN GROUPING(g.genre_name) = 1 THEN 'All Genres' ELSE g.genre_name END AS genre_name,
    COUNT(f.rating_id) AS total_views,
    ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS avg_rating
FROM dw.FactRating f
JOIN dw.DimUser u ON u.user_key = f.user_key
JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
JOIN dw.DimGenre g ON g.genre_key = b.genre_key
GROUP BY CUBE (u.gender, u.age_group, g.genre_name)
ORDER BY u.gender, u.age_group, g.genre_name;
GO

-- ============================================================================
-- 4. OLAP OPERATION: DRILL-DOWN (FROM YEAR TO QUARTER TO MONTH)
-- Demonstrates navigating from summary level down to detailed monthly view
-- ============================================================================
PRINT '=== 4. OLAP DRILL-DOWN (YEAR 2000 -> QUARTER -> MONTH) ===';

SELECT 
    d.[year],
    d.[quarter],
    d.[month],
    d.month_name,
    g.genre_name,
    COUNT(f.rating_id) AS total_views,
    ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS avg_rating
FROM dw.FactRating f
JOIN dw.DimDate d ON d.date_key = f.date_key
JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
JOIN dw.DimGenre g ON g.genre_key = b.genre_key
WHERE d.[year] = 2000 AND g.genre_name IN ('Action', 'Comedy', 'Drama')
GROUP BY d.[year], d.[quarter], d.[month], d.month_name, g.genre_name
ORDER BY d.[quarter], d.[month], g.genre_name;
GO

-- ============================================================================
-- 5. OLAP OPERATION: ROLL-UP (FROM MONTH TO YEAR)
-- Demonstrates aggregating monthly sales up to full-year totals
-- ============================================================================
PRINT '=== 5. OLAP ROLL-UP (MONTHLY TO ANNUAL TOTALS) ===';

SELECT 
    d.[year],
    g.genre_name,
    COUNT(f.rating_id) AS annual_views,
    ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS avg_rating,
    ROUND(SUM(CAST(f.watch_minutes AS BIGINT)) / 60.0, 1) AS total_watch_hours
FROM dw.FactRating f
JOIN dw.DimDate d ON d.date_key = f.date_key
JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
JOIN dw.DimGenre g ON g.genre_key = b.genre_key
GROUP BY d.[year], g.genre_name
ORDER BY d.[year], annual_views DESC;
GO

-- ============================================================================
-- 6. OLAP OPERATION: SLICE (FIXING ONE DIMENSION: GENRE = 'Action')
-- Analyzes the 2D plane (Year x Age Group) for Action movies
-- ============================================================================
PRINT '=== 6. OLAP SLICE (GENRE = Action) ===';

SELECT 
    d.[year],
    u.age_group,
    COUNT(f.rating_id) AS action_views,
    ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS avg_rating
FROM dw.FactRating f
JOIN dw.DimDate d ON d.date_key = f.date_key
JOIN dw.DimUser u ON u.user_key = f.user_key
JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
JOIN dw.DimGenre g ON g.genre_key = b.genre_key
WHERE g.genre_name = 'Action'
GROUP BY d.[year], u.age_group
ORDER BY d.[year], u.age_group;
GO

-- ============================================================================
-- 7. OLAP OPERATION: DICE (SUB-CUBE SELECTION)
-- Time IN (2001, 2002) AND Genre IN ('Action', 'Drama') AND Gender = 'Female'
-- ============================================================================
PRINT '=== 7. OLAP DICE (SUB-CUBE FILTER) ===';

SELECT 
    d.[year],
    d.[quarter],
    g.genre_name,
    u.gender,
    u.age_group,
    COUNT(f.rating_id) AS views,
    ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS avg_rating
FROM dw.FactRating f
JOIN dw.DimDate d ON d.date_key = f.date_key
JOIN dw.DimUser u ON u.user_key = f.user_key
JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
JOIN dw.DimGenre g ON g.genre_key = b.genre_key
WHERE d.[year] IN (2001, 2002)
  AND g.genre_name IN ('Action', 'Drama')
  AND u.gender = 'Female'
GROUP BY d.[year], d.[quarter], g.genre_name, u.gender, u.age_group
ORDER BY d.[year], d.[quarter], g.genre_name, u.age_group;
GO

-- ============================================================================
-- 8. OLAP OPERATION: PIVOT (ROTATING QUARTERS INTO COLUMNS)
-- Provides crosstab matrix of Total Views across quarters for each genre
-- ============================================================================
PRINT '=== 8. OLAP PIVOT (QUARTERS AS COLUMNS) ===';

WITH PivotSource AS (
    SELECT 
        g.genre_name,
        'Y' + CAST(d.[year] AS VARCHAR) + '_Q' + CAST(d.[quarter] AS VARCHAR) AS period,
        f.rating_id
    FROM dw.FactRating f
    JOIN dw.DimDate d ON d.date_key = f.date_key
    JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
    JOIN dw.DimGenre g ON g.genre_key = b.genre_key
    WHERE d.[year] IN (2000, 2001, 2002)
)
SELECT 
    genre_name,
    ISNULL([Y2000_Q2], 0) AS [2000_Q2],
    ISNULL([Y2000_Q3], 0) AS [2000_Q3],
    ISNULL([Y2000_Q4], 0) AS [2000_Q4],
    ISNULL([Y2001_Q1], 0) AS [2001_Q1],
    ISNULL([Y2001_Q2], 0) AS [2001_Q2],
    ISNULL([Y2001_Q3], 0) AS [2001_Q3],
    ISNULL([Y2001_Q4], 0) AS [2001_Q4],
    ISNULL([Y2002_Q1], 0) AS [2002_Q1],
    ISNULL([Y2002_Q2], 0) AS [2002_Q2],
    ISNULL([Y2002_Q3], 0) AS [2002_Q3],
    ISNULL([Y2002_Q4], 0) AS [2002_Q4]
FROM (
    SELECT genre_name, period, rating_id FROM PivotSource
) src
PIVOT (
    COUNT(rating_id)
    FOR period IN (
        [Y2000_Q2], [Y2000_Q3], [Y2000_Q4],
        [Y2001_Q1], [Y2001_Q2], [Y2001_Q3], [Y2001_Q4],
        [Y2002_Q1], [Y2002_Q2], [Y2002_Q3], [Y2002_Q4]
    )
) pvt
ORDER BY genre_name;
GO
