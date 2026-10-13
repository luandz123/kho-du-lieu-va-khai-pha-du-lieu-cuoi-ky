-- ============================================================================
-- 05_views_for_powerbi.sql
-- Project: Movie Data Warehouse & Data Mining
-- Description: Clean, denormalized, and high-performance SQL views designed
--              specifically for Power BI Desktop data modeling and dashboards.
-- ============================================================================

USE MovieDW;
GO

-- 1. VIEW: FACT RATING WITH CORE DIMENSIONS
-- Primary analytical view connecting Fact with User, Movie, Director, and Date
IF OBJECT_ID('dw.V_PowerBI_FactRating', 'V') IS NOT NULL DROP VIEW dw.V_PowerBI_FactRating;
GO

CREATE VIEW dw.V_PowerBI_FactRating AS
SELECT 
    f.rating_id,
    f.user_key,
    u.user_id,
    u.gender,
    u.age_group,
    u.occupation_name,
    f.movie_key,
    m.movie_id,
    m.title AS movie_title,
    m.release_year,
    m.runtime_minutes,
    d.director_name,
    f.date_key,
    dt.full_date,
    dt.[year],
    dt.[quarter],
    dt.[month],
    dt.month_name,
    dt.is_weekend,
    f.rating,
    f.watch_minutes,
    ROUND(f.watch_minutes / 60.0, 2) AS watch_hours,
    f.is_simulated
FROM dw.FactRating f
JOIN dw.DimUser u ON u.user_key = f.user_key
JOIN dw.DimMovie m ON m.movie_key = f.movie_key
JOIN dw.DimDirector d ON d.director_key = m.director_key
JOIN dw.DimDate dt ON dt.date_key = f.date_key;
GO

-- 2. VIEW: GENRE QUARTERLY PERFORMANCE
-- Multi-genre performance aggregated by time for Page 3 (Genre Trends)
IF OBJECT_ID('dw.V_PowerBI_GenrePerformance', 'V') IS NOT NULL DROP VIEW dw.V_PowerBI_GenrePerformance;
GO

CREATE VIEW dw.V_PowerBI_GenrePerformance AS
SELECT 
    dt.[year],
    dt.[quarter],
    CAST(dt.[year] AS VARCHAR) + '-Q' + CAST(dt.[quarter] AS VARCHAR) AS period,
    dt.[month],
    dt.month_name,
    g.genre_name,
    COUNT(f.rating_id) AS total_views,
    ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS avg_rating,
    ROUND(SUM(CAST(f.watch_minutes AS BIGINT)) / 60.0, 1) AS total_watch_hours
FROM dw.FactRating f
JOIN dw.DimDate dt ON dt.date_key = f.date_key
JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
JOIN dw.DimGenre g ON g.genre_key = b.genre_key
GROUP BY dt.[year], dt.[quarter], dt.[month], dt.month_name, g.genre_name;
GO

-- 3. VIEW: USER DEMOGRAPHICS SUMMARY
-- Demographic distribution with total activity for Page 2
IF OBJECT_ID('dw.V_PowerBI_UserDemographics', 'V') IS NOT NULL DROP VIEW dw.V_PowerBI_UserDemographics;
GO

CREATE VIEW dw.V_PowerBI_UserDemographics AS
SELECT 
    u.user_id,
    u.gender,
    u.age_code,
    u.age_group,
    u.occupation_name,
    COUNT(f.rating_id) AS total_ratings_given,
    ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS user_avg_rating,
    ROUND(SUM(CAST(f.watch_minutes AS BIGINT)) / 60.0, 1) AS user_total_watch_hours
FROM dw.DimUser u
LEFT JOIN dw.FactRating f ON f.user_key = u.user_key
GROUP BY u.user_id, u.gender, u.age_code, u.age_group, u.occupation_name;
GO

-- 4. VIEW: DIRECTOR RANKINGS & PERFORMANCE
-- Evaluates director popularity and critical acclaim for Page 4
IF OBJECT_ID('dw.V_PowerBI_DirectorRankings', 'V') IS NOT NULL DROP VIEW dw.V_PowerBI_DirectorRankings;
GO

CREATE VIEW dw.V_PowerBI_DirectorRankings AS
SELECT 
    d.director_name,
    COUNT(DISTINCT m.movie_id) AS total_directed_movies,
    COUNT(f.rating_id) AS total_ratings_received,
    ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS director_avg_rating,
    ROUND(SUM(CAST(f.watch_minutes AS BIGINT)) / 60.0, 1) AS total_watch_hours_generated
FROM dw.DimDirector d
JOIN dw.DimMovie m ON m.director_key = d.director_key
JOIN dw.FactRating f ON f.movie_key = m.movie_key
WHERE d.director_name <> 'Unknown'
GROUP BY d.director_name;
GO

PRINT '[SUCCESS] Created 4 Power BI views in dw schema.';
GO
