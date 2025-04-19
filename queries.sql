SELECT * FROM user_server_rank lIMIT 3
-- Create the table
CREATE TABLE sample_data (
    id INTEGER PRIMARY KEY,
    active BOOLEAN,
    name TEXT,
    created_at TIMESTAMP
);

-- Insert 100 random records
INSERT INTO sample_data (active, name, created_at)
WITH RECURSIVE random_data(n, active, name, created_at) AS (
    SELECT
        1,
        CASE WHEN random() % 2 = 0 THEN 1 ELSE 0 END,
        'User_' || hex(randomblob(4)),
        datetime(unixepoch() - (random() % 31536000), 'unixepoch')
    UNION ALL
    SELECT
        n + 1,
        CASE WHEN random() % 2 = 0 THEN 1 ELSE 0 END,
        'User_' || hex(randomblob(4)),
        datetime(unixepoch() - (random() % 31536000), 'unixepoch')
    FROM random_data
    WHERE n < 100
)
SELECT active, name, created_at FROM random_data;

-- Verify data was inserted
SELECT * FROM sample_data;
SELECT * FROM server_user_rank LIMIT 3;
SELECT * FROM server_user_rank LIMIT 3;

SELECT * FROM sample_data
SELECT * FROM server_user_rank
SELECT * FROM user_rank_run
SELECT * FROM user_run
\d+
.tables
SELECT
