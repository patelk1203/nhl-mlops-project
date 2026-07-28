-- This script will run automatically when the database container starts for the first time.

CREATE TABLE IF NOT EXISTS nhl_games (
    game_id INT PRIMARY KEY,
    season INT,
    game_date DATE,
    venue VARCHAR(255),
    home_team VARCHAR(10),
    away_team VARCHAR(10),
    home_score INT,
    away_score INT
);