SELECT *
FROM strength_db.strength
;

SELECT *
FROM strength_db.sessions
;

SELECT *
FROM strength_db.exercise_lookup
;

-- Just look at strength training sessions
SELECT * FROM sessions
WHERE session_type = "strength";

-- Join session ID between sessions and strength dbs
SELECT date, exercise_id, load_kg,  reps, rpe, e1rm
FROM sessions
INNER JOIN strength
ON strength.session_id = sessions.session_id
;

-- Join tables strength and exercise lookup on exercise_id to get the exercise names
SELECT exercise_name, load_kg,  reps, rpe, e1rm
FROM strength
INNER JOIN exercise_lookup
ON strength.exercise_id = exercise_lookup.exercise_id
;