SELECT CASE WHEN device = 0 THEN 'desktop'
            WHEN device = 1 THEN 'mobile'
            WHEN device = 2 THEN 'tablet'
       END,
       round(avg_resp_clicks, 2)
  FROM (
      SELECT count(a.sessionid) OVER w AS count,
             b.device AS device,
             avg(resp_clicks) OVER w AS avg_resp_clicks
        FROM clicks a INNER JOIN sessions b ON (a.sessionid = b.sessionid)
        WINDOW w AS (PARTITION BY a.sessionid) ) AS foo
  WHERE count > 1
  ORDER BY avg_resp_clicks DESC;
