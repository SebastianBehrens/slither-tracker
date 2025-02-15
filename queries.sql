SELECT * FROM server_user_rank LIMIT 3;

PRAGMA table_info(server_user_rank);

WITH time_now AS (
    SELECT
        MAX(created_at) as time_now
    FROM
        server_user_rank
)
    SELECT
        MAX(created_at) as time_prev
    FROM
        server_user_rank
    WHERE
        created_at < (SELECT time_now FROM time_now)
)
SELECT
    now.server_id,
    now.server_time,
    now.nick,
    prev.score as score_prev,
    now.score AS score_now
FROM
    server_user_rank now
LEFT JOIN
    server_user_rank prev
ON
    now.server_id = prev.server_id
AND now.server_time = prev.server_time
AND now.nick = prev.nick
ORDER BY
    now.server_id,
    now.server_time,
    now.nick;
