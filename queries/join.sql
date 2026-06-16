SELECT
    w.date,
    w.weight,
    b.bodyfat
FROM weight w
INNER JOIN bodyfat b
    ON w.date = b.date
ORDER BY w.date;