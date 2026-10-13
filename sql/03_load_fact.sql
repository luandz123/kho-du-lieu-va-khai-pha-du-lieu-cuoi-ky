-- ============================================================================
-- 03_load_fact.sql
-- Project: Movie Data Warehouse & Data Mining
-- Description: Transforms and populates dw.FactRating by resolving surrogate keys
--              from dimension tables.
-- ============================================================================

USE MovieDW;
GO

PRINT '[INFO] Loading dw.FactRating...';

-- Clear existing data if re-running
TRUNCATE TABLE dw.FactRating;

-- Insert fact records with surrogate key lookups
INSERT INTO dw.FactRating (user_key, movie_key, date_key, rating, watch_minutes, is_simulated)
SELECT 
    u.user_key,
    m.movie_key,
    r.date_key,
    r.rating,
    r.watch_minutes,
    ISNULL(r.is_simulated, 1)
FROM stg.Ratings r
JOIN dw.DimUser u ON u.user_id = r.user_id
JOIN dw.DimMovie m ON m.movie_id = r.movie_id
JOIN dw.DimDate d ON d.date_key = r.date_key;

PRINT '[SUCCESS] Loaded dw.FactRating: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' rows.';
GO
