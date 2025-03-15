SELECT COUNT(*) FROM server_user_rank LIMIT 3;

SELECT * FROM server_user_rank LIMIT 3;

CREATE TABLE tmp AS
    SELECT
        server_id
        , server_time
        , TRUE AS flg_active
        , nick
        , score
        , created_at
    FROM
        server_user_rank


DROP TABLE server_user_rank
DROP TABLE tmp
DELETE FROM server_user_rank

-- SELECT DISTINCT
-- created_at
-- FROM
-- server_user_rank
-- ORDER BY created_at

-- SELECT *
-- FROM
-- server_user_rank
-- fetch_row_count
-- SELECT SUMoSELECT SUM(pgsize) FROM dbstat WHERE name = 'your_table_name';
-- SELECT SUM(pgsize)/(1024.0*1024.0) FROM dbstat WHERE name = 'server_user_rank';

-- PRAGMA table_info(server_user_rank);


SELECT
server_id
, COUNT(DISTINCT nick) AS nick_count
, COUNT(DISTINCT created_at) AS timestamp_count
FROM
server_user_rank
GROUP BY server_id
ORDER BY nick_count DESC, timestamp_count DESC

SELECT * FROM server_user_rank WHERE server_id = 2891
SELECT * FROM server_user_rank

-- mine
WITH time_now AS (
    SELECT
        MAX(created_at) as time
    FROM
        server_user_rank
), time_last AS (
    SELECT
        MAX(created_at) as time
    FROM
        server_user_rank
    WHERE
        created_at < (SELECT time FROM time_now)
), users_traced AS (
    SELECT
        dlast.server_id
        ,dlast.server_time AS server_time_now
        ,dlast.nick
        ,dlast.score AS score_now
        ,dlast.rank  AS rank_now
        ,dnow.server_time AS server_time_last
        ,dnow.score AS score_last
        ,dnow.rank AS rank_last
    FROM
        server_user_rank dlast
    FULL OUTER JOIN
       server_user_rank dnow
    ON
       dnow.created_at = (SELECT time FROM time_now)
    AND
       dnow.server_id = dlast.server_id
    AND
       dnow.nick = dlast.nick
    WHERE
        dlast.created_at = (SELECT time from time_last)
    AND
        LENGTH(TRIM(dlast.nick)) > 0
    AND
        dlast.server_id='test_server_1'
    AND
        dlast.flg_active = 1
), users_new AS (
    SELECT
        trace.server_id
        ,trace.server_time AS server_time_now
        ,trace.nick
        ,trace.score AS score_now
        ,trace.rank  AS rank_now
        ,trace.server_time AS server_time_last
        ,trace.score AS score_last
        ,trace.rank AS rank_last
    FROM
        users_traced
    UNION ALL
    SELECT
        new.server_id
        ,new.server_time AS server_time_now
        ,new.nick
        ,new.score AS score_now
        ,new.rank  AS rank_now
        ,NULL AS server_time_last
        ,NULL AS score_last
        ,NULL AS rank_last
    FROM
        server_user_rank new
    LEFT JOIN
       server_user_rank anti
    ON
       anti.created_at = (SELECT time FROM time_last)
    AND
       anti.server_id = new.server_id
    AND
       new.nick = anti.nick
    WHERE
        new.created_at = (SELECT time from time_now)
    AND
        anti.nick IS NULL
)
SELECT * FROM users_new

SELECT
    server_id
    ,server_time_last
    ,server_time_now
    ,nick
    ,score_last
    ,score_now
    ,rank_last
    ,rank_now
    ,score_now-score_last AS delta_score
    ,rank_now-rank_last AS delta_rank
FROM
    delta_data


SELECT
*
FROM
    server_user_rank
WHERE
    server_id = 2220
AND server_time > '2025-02-15T22:00:00+00'



    --- suggestion AI
WITH time_now AS (
    SELECT
        MAX(created_at) as time
    FROM
        server_user_rank
), time_last AS (
    SELECT
        MAX(created_at) as time
    FROM
        server_user_rank
    WHERE
        created_at < (SELECT time FROM time_now)
), delta_data AS (
SELECT
    dlast.server_id
    ,dlast.server_time AS server_time_now
    ,dlast.nick
    ,dlast.score AS score_now
    ,dlast.rank  AS rank_now
    ,dnow.server_time AS server_time_last
    ,dnow.score AS score_last
    ,dnow.rank AS rank_last
FROM
    server_user_rank dlast
FULL OUTER JOIN
   server_user_rank dnow
ON
   dnow.server_id = dlast.server_id
AND
   dnow.nick = dlast.nick
WHERE
    (dlast.created_at = (SELECT time FROM time_last) OR dlast.created_at IS NULL)
AND
    (dnow.created_at = (SELECT time FROM time_now) OR dnow.created_at IS NULL)
)
SELECT
    server_id
    ,server_time_last
    ,server_time_now
    ,score_last
    ,score_now
    ,rank_last
    ,rank_now
    ,score_now - score_last AS delta_score
    ,rank_now - rank_last AS delta_rank
FROM
    delta_data
WHERE
    server_id = 2220






WITH RankChanges AS (
  SELECT
    server_id,
    nick,
    server_time,
    rank,
    LEAD(server_time) OVER (
        PARTITION BY
        server_id
        , nick
        ORDER BY server_time
        ) AS next_time
  FROM server_user_rank
)
SELECT
  server_id,
  nick,
  rank,
  server_time as rank_start,
  next_time as rank_end,
  (julianday(next_time) - julianday(server_time)) * 24.0 * 60.0 * 60.0 as seconds_at_rank
FROM RankChanges
  WHERE next_time IS NOT NULL  -- Only include completed stints
ORDER BY server_id, nick, rank, server_time;



