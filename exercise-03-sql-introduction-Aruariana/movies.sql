-- TODO: Create the tables and import the data from the tsv files here.
-- For each file you should first create a table with an appropriate schema, e.g. using
--     CREATE TABLE test(some_id INTEGER PRIMARY KEY, some_text TEXT)
-- and afterwards populate the table with data from your tsv file using
--     .import test.tsv test
-- where test.tsv has two tab-separated columns, the first one containing integers,
-- and the second one containing text.
-- Don't forget to set the correct separator before importing your data.
CREATE TABLE movies(id TEXT PRIMARY KEY, title TEXT, year INTEGER, score REAL);
CREATE TABLE people(id TEXT PRIMARY KEY, name TEXT);
CREATE TABLE cast(movie_id TEXT REFERENCES movies(id), people_id TEXT REFERENCES people(id), role TEXT, job TEXT);
CREATE TABLE oscars(movie_id TEXT REFERENCES movies(id), people_id TEXT REFERENCES people(id), category TEXT);
.separator "\t"
.import movies.tsv movies
.import people.tsv people
.import cast.tsv cast
.import oscars.tsv oscars