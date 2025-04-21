-- make sqlite3 output prettier tables
.headers ON
.mode column

.print \nIn which YEAR was Titanic released AND what rating ON IMDb does it have?\n

-- TODO: add the SQL query for the first question here

SELECT year, score FROM movies WHERE title='Titanic';

.print \nWho directed Fargo?\n

-- TODO: add the SQL query for the second question here

SELECT name FROM movies, people, cast WHERE movies.id = movie_id AND people.id = people_id AND job='director' AND movies.title='Fargo';

.print \nWhich actors won Oscars FOR which roles IN which movies AND IN which categories?\n

-- TODO: add the SQL query for the third question here

SELECT name, role, title, category FROM movies, people, cast, oscars WHERE movies.id = "cast".movie_id AND people.id = "cast".people_id AND movies.id = oscars.movie_id AND people.id = oscars.people_id AND job='actor';

-- OPTIONAL: add more questions and SQL queries here
