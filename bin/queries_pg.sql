SELECT * FROM public.server_user_rank
SELECT DISTINCT created_at FROM public.server_user_rank
SELECT * FROM public.user_rank_runs
SELECT * FROM public.server_user_rank LIMIT 3
TRUNCATE public.server_user_rank

TRUNCATE TABLE public.user_run
SELECT * FROm public.user_run


SELECT *
FROM user_run
WHERE 1=1
AND duration_seconds IS NOT NULL
AND nick NOT LIKE ''
ORDER BY duration_seconds DESC LIMIT 1000;

SELECT
*
FROM
user_run
WHERE duration_seconds IS NOT NULL
AND nick != 'NTL.bot'
ORDER BY max_score DESC LIMIT 1000;

SELECT
min_rank
,nick
,duration_seconds
,start_time
FROM public.user_run
WHERE duration_seconds IS NOT NULL
AND nick NOT LIKE ''
AND nick NOT LIKE '%NTL.bot%'
ORDER BY duration_seconds DESC
LIMIT 3;
