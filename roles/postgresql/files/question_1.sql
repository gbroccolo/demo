WITH dev AS (
    SELECT device,
           count(*) AS count
      FROM sessions
    GROUP BY device)
SELECT device,
       max(count) OVER (PARTITION BY device)
  FROM dev LIMIT 1;
