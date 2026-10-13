-- ============================================================================
-- 02_load_dims.sql
-- Project: Movie Data Warehouse & Data Mining
-- Description: Transforms and populates dimension tables and bridge tables
--              from the staging (stg) schema.
-- ============================================================================

USE MovieDW;
GO

-- 1. LOAD DimUser
PRINT '[INFO] Loading dw.DimUser...';
INSERT INTO dw.DimUser (user_id, gender, age_code, age_group, occupation_id, occupation_name, zip_code)
SELECT DISTINCT
    user_id,
    ISNULL(gender, 'Unknown'),
    ISNULL(age_code, 0),
    ISNULL(age_group, 'Unknown'),
    ISNULL(occupation_id, 0),
    ISNULL(occupation_name, 'Other'),
    zip_code
FROM stg.Users u
WHERE NOT EXISTS (SELECT 1 FROM dw.DimUser d WHERE d.user_id = u.user_id);
PRINT '[SUCCESS] Loaded dw.DimUser: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' rows.';
GO

-- 2. LOAD DimDirector
PRINT '[INFO] Loading dw.DimDirector...';
-- Ensure 'Unknown' is present
IF NOT EXISTS (SELECT 1 FROM dw.DimDirector WHERE director_name = 'Unknown')
    INSERT INTO dw.DimDirector (director_name) VALUES ('Unknown');

-- Insert distinct directors from staging
INSERT INTO dw.DimDirector (director_name)
SELECT DISTINCT LTRIM(RTRIM(director))
FROM stg.Movies
WHERE director IS NOT NULL AND LTRIM(RTRIM(director)) <> '' AND LTRIM(RTRIM(director)) <> 'Unknown'
  AND NOT EXISTS (
      SELECT 1 FROM dw.DimDirector d 
      WHERE d.director_name = LTRIM(RTRIM(stg.Movies.director))
  );
PRINT '[SUCCESS] Loaded dw.DimDirector: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' new rows.';
GO

-- 3. LOAD DimGenre
PRINT '[INFO] Loading dw.DimGenre...';
INSERT INTO dw.DimGenre (genre_key, genre_name)
SELECT DISTINCT genre_key, genre_name
FROM stg.Genres g
WHERE NOT EXISTS (SELECT 1 FROM dw.DimGenre d WHERE d.genre_key = g.genre_key);
PRINT '[SUCCESS] Loaded dw.DimGenre: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' rows.';
GO

-- 4. LOAD DimMovie
PRINT '[INFO] Loading dw.DimMovie...';
INSERT INTO dw.DimMovie (movie_id, title, raw_title, release_year, runtime_minutes, director_key, imdb_tconst, match_type)
SELECT 
    m.movie_id,
    m.title,
    m.raw_title,
    m.release_year,
    ISNULL(m.runtime_minutes, 95),
    ISNULL(dir.director_key, (SELECT director_key FROM dw.DimDirector WHERE director_name = 'Unknown')),
    m.imdb_tconst,
    ISNULL(m.match_type, 'UNMATCHED')
FROM stg.Movies m
LEFT JOIN dw.DimDirector dir ON dir.director_name = LTRIM(RTRIM(m.director))
WHERE NOT EXISTS (SELECT 1 FROM dw.DimMovie dm WHERE dm.movie_id = m.movie_id);
PRINT '[SUCCESS] Loaded dw.DimMovie: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' rows.';
GO

-- 5. LOAD BridgeMovieGenre
PRINT '[INFO] Loading dw.BridgeMovieGenre...';
INSERT INTO dw.BridgeMovieGenre (movie_key, genre_key)
SELECT DISTINCT
    dm.movie_key,
    mg.genre_key
FROM stg.MovieGenre mg
JOIN dw.DimMovie dm ON dm.movie_id = mg.movie_id
JOIN dw.DimGenre dg ON dg.genre_key = mg.genre_key
WHERE NOT EXISTS (
    SELECT 1 FROM dw.BridgeMovieGenre b
    WHERE b.movie_key = dm.movie_key AND b.genre_key = mg.genre_key
);
PRINT '[SUCCESS] Loaded dw.BridgeMovieGenre: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' rows.';
GO

-- 6. LOAD DimDate
PRINT '[INFO] Loading dw.DimDate...';
INSERT INTO dw.DimDate (date_key, full_date, [year], [quarter], [month], month_name, [day], day_of_week, day_name, is_weekend)
SELECT DISTINCT
    date_key,
    full_date,
    [year],
    [quarter],
    [month],
    month_name,
    [day],
    day_of_week,
    day_name,
    is_weekend
FROM stg.Dates dt
WHERE NOT EXISTS (SELECT 1 FROM dw.DimDate d WHERE d.date_key = dt.date_key);
PRINT '[SUCCESS] Loaded dw.DimDate: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' rows.';
GO
