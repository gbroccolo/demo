SELECT sessionid,
       mouse_distance
  FROM mouse_moves
ORDER BY mouse_distance DESC
  LIMIT 1;
