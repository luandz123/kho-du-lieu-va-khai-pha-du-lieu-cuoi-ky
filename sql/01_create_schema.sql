-- ============================================================================
-- 01_create_schema.sql
-- Project: Movie Data Warehouse & Data Mining
-- Description: Creates staging (stg) and warehouse (dw) schemas, tables,
--              constraints, and OLAP query optimization indexes.
-- ============================================================================

USE MovieDW;
GO

-- 1. CREATE SCHEMAS
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'stg')
    EXEC('CREATE SCHEMA stg');
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'dw')
    EXEC('CREATE SCHEMA dw');
GO

-- 2. DROP EXISTING TABLES IN REVERSE DEPENDENCY ORDER
IF OBJECT_ID('dw.FactRating', 'U') IS NOT NULL DROP TABLE dw.FactRating;
IF OBJECT_ID('dw.BridgeMovieGenre', 'U') IS NOT NULL DROP TABLE dw.BridgeMovieGenre;
IF OBJECT_ID('dw.DimMovie', 'U') IS NOT NULL DROP TABLE dw.DimMovie;
IF OBJECT_ID('dw.DimDirector', 'U') IS NOT NULL DROP TABLE dw.DimDirector;
IF OBJECT_ID('dw.DimGenre', 'U') IS NOT NULL DROP TABLE dw.DimGenre;
IF OBJECT_ID('dw.DimDate', 'U') IS NOT NULL DROP TABLE dw.DimDate;
IF OBJECT_ID('dw.DimUser', 'U') IS NOT NULL DROP TABLE dw.DimUser;

-- Drop Staging Tables
IF OBJECT_ID('stg.Ratings', 'U') IS NOT NULL DROP TABLE stg.Ratings;
IF OBJECT_ID('stg.MovieGenre', 'U') IS NOT NULL DROP TABLE stg.MovieGenre;
IF OBJECT_ID('stg.Movies', 'U') IS NOT NULL DROP TABLE stg.Movies;
IF OBJECT_ID('stg.Users', 'U') IS NOT NULL DROP TABLE stg.Users;
IF OBJECT_ID('stg.Dates', 'U') IS NOT NULL DROP TABLE stg.Dates;
IF OBJECT_ID('stg.Genres', 'U') IS NOT NULL DROP TABLE stg.Genres;
IF OBJECT_ID('stg.Directors', 'U') IS NOT NULL DROP TABLE stg.Directors;
GO

-- ============================================================================
-- 3. CREATE STAGING TABLES (stg)
-- ============================================================================

CREATE TABLE stg.Users (
    user_id INT NOT NULL,
    gender VARCHAR(10) NULL,
    age_code INT NULL,
    age_group VARCHAR(20) NULL,
    occupation_id INT NULL,
    occupation_name VARCHAR(100) NULL,
    zip_code VARCHAR(20) NULL
);
GO

CREATE TABLE stg.Directors (
    director_key INT NOT NULL,
    director_name NVARCHAR(200) NOT NULL
);
GO

CREATE TABLE stg.Genres (
    genre_key INT NOT NULL,
    genre_name VARCHAR(50) NOT NULL
);
GO

CREATE TABLE stg.Movies (
    movie_id INT NOT NULL,
    title NVARCHAR(300) NOT NULL,
    raw_title NVARCHAR(300) NULL,
    release_year INT NULL,
    genres VARCHAR(200) NULL,
    runtime_minutes INT NULL,
    director NVARCHAR(200) NULL,
    imdb_tconst VARCHAR(20) NULL,
    match_type VARCHAR(20) NULL
);
GO

CREATE TABLE stg.MovieGenre (
    movie_id INT NOT NULL,
    genre_key INT NOT NULL
);
GO

CREATE TABLE stg.Dates (
    date_key INT NOT NULL,
    full_date DATE NOT NULL,
    [year] INT NOT NULL,
    [quarter] INT NOT NULL,
    [month] INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    [day] INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BIT NOT NULL
);
GO

CREATE TABLE stg.Ratings (
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    date_key INT NOT NULL,
    rating_date DATE NOT NULL,
    rating TINYINT NOT NULL,
    watch_minutes INT NOT NULL,
    is_simulated BIT NOT NULL DEFAULT 1
);
GO

-- ============================================================================
-- 4. CREATE WAREHOUSE TABLES (dw) - STAR SCHEMA
-- ============================================================================

-- DimUser: Stores demographic attributes
CREATE TABLE dw.DimUser (
    user_key INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    gender VARCHAR(10) NOT NULL,
    age_code INT NOT NULL,
    age_group VARCHAR(20) NOT NULL,
    occupation_id INT NOT NULL,
    occupation_name VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20) NULL
);
GO

-- DimDirector: Stores distinct directors extracted from IMDb
CREATE TABLE dw.DimDirector (
    director_key INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    director_name NVARCHAR(200) NOT NULL UNIQUE
);
GO

-- DimGenre: Stores standard movie genres
CREATE TABLE dw.DimGenre (
    genre_key INT NOT NULL PRIMARY KEY,
    genre_name VARCHAR(50) NOT NULL UNIQUE
);
GO

-- DimMovie: Stores movie catalog enriched with IMDb metadata
CREATE TABLE dw.DimMovie (
    movie_key INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    movie_id INT NOT NULL UNIQUE,
    title NVARCHAR(300) NOT NULL,
    raw_title NVARCHAR(300) NULL,
    release_year INT NULL,
    runtime_minutes INT NOT NULL DEFAULT 95,
    director_key INT NOT NULL,
    imdb_tconst VARCHAR(20) NULL,
    match_type VARCHAR(20) NOT NULL DEFAULT 'UNMATCHED',
    CONSTRAINT FK_DimMovie_DimDirector FOREIGN KEY (director_key) REFERENCES dw.DimDirector(director_key)
);
GO

-- BridgeMovieGenre: Resolves M:N relationship between Movie and Genre
CREATE TABLE dw.BridgeMovieGenre (
    movie_key INT NOT NULL,
    genre_key INT NOT NULL,
    CONSTRAINT PK_BridgeMovieGenre PRIMARY KEY (movie_key, genre_key),
    CONSTRAINT FK_Bridge_DimMovie FOREIGN KEY (movie_key) REFERENCES dw.DimMovie(movie_key),
    CONSTRAINT FK_Bridge_DimGenre FOREIGN KEY (genre_key) REFERENCES dw.DimGenre(genre_key)
);
GO

-- DimDate: Time dimension hierarchy (Day -> Month -> Quarter -> Year)
CREATE TABLE dw.DimDate (
    date_key INT NOT NULL PRIMARY KEY,
    full_date DATE NOT NULL,
    [year] INT NOT NULL,
    [quarter] INT NOT NULL,
    [month] INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    [day] INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BIT NOT NULL
);
GO

-- FactRating: Central event table (Grain: 1 rating event per user per movie on a date)
CREATE TABLE dw.FactRating (
    rating_id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    user_key INT NOT NULL,
    movie_key INT NOT NULL,
    date_key INT NOT NULL,
    rating TINYINT NOT NULL,
    watch_minutes INT NOT NULL,
    is_simulated BIT NOT NULL DEFAULT 1,
    CONSTRAINT FK_FactRating_DimUser FOREIGN KEY (user_key) REFERENCES dw.DimUser(user_key),
    CONSTRAINT FK_FactRating_DimMovie FOREIGN KEY (movie_key) REFERENCES dw.DimMovie(movie_key),
    CONSTRAINT FK_FactRating_DimDate FOREIGN KEY (date_key) REFERENCES dw.DimDate(date_key)
);
GO

-- ============================================================================
-- 5. PERFORMANCE INDEXES FOR STAR-JOIN & OLAP OPERATIONS
-- ============================================================================

-- FactRating Foreign Key Indexes: Drastically speeds up Star joins between Fact and Dims
CREATE NONCLUSTERED INDEX IX_FactRating_UserKey ON dw.FactRating(user_key)
    INCLUDE (rating, watch_minutes);
CREATE NONCLUSTERED INDEX IX_FactRating_MovieKey ON dw.FactRating(movie_key)
    INCLUDE (rating, watch_minutes);
CREATE NONCLUSTERED INDEX IX_FactRating_DateKey ON dw.FactRating(date_key)
    INCLUDE (rating, watch_minutes);

-- FactRating Rating Index: Supports filtering high-rating movies for association rules & recommendations
CREATE NONCLUSTERED INDEX IX_FactRating_Rating ON dw.FactRating(rating);

-- BridgeMovieGenre Index: Accelerates multi-genre aggregations and genre slicers
CREATE NONCLUSTERED INDEX IX_Bridge_GenreKey ON dw.BridgeMovieGenre(genre_key, movie_key);

-- DimDate Year-Quarter Index: Optimized for QoQ window function LAG() and time roll-ups
CREATE NONCLUSTERED INDEX IX_DimDate_Year_Quarter ON dw.DimDate([year], [quarter])
    INCLUDE (month_name, full_date);

-- DimMovie Director Index: Optimizes filtering by director
CREATE NONCLUSTERED INDEX IX_DimMovie_DirectorKey ON dw.DimMovie(director_key);
GO
