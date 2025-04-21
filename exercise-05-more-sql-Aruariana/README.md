[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/zyvMYpYN)
# Data Bases and Information Systems - Exercise Sheet 5  
Prof. Dr. Joschka Bödecker, Julien Brosseit, Daniel Jost

![introduction image](./images/more_sql.png)

Exercise developed by **Prof. Dr. Hannah Bast and Team** with slight modifications  
Submit until **Wednesday, 4 December 2024**

_Before the starting the exercise_: Download the _persons_ TSV file containing the table data from our [ILIAS](https://ilias.uni-freiburg.de/goto.php?target=fold_3701675&client_id=unifreiburg) course.

## Exercise 1
For the query

_All movies that won an Oscar (in any category) and were released in 2000, 2001, 2002, or 2003_

think of two different sequences of operations and enter them as code into _run sequence 1_ and
_run sequence 2_ into `queries.py`. Make sure their output equals that of SQLite3.

Then, for both sequences, calculate their estimated cost using the simple cost estimates described
in lecture 4 and at the beginning of lecture 5. You can do that either in _calc cost 1_ and _calc cost 2_
with code (use the _shape_ attribute of the _Table_ class to get the dimensions of a table) or by hand.
If you do it by hand, write down your calculations for each sequence in your experciences.md and
make sure to return your final cost estimates in _calc cost 1_ and _calc cost 2_.

Finally, run the script with `python queries.py *.tsv --exercise 1` to see how well the cost estimates
reflect real runtimes and document your findings in `experiences.md`.

## Exercise 2
In `operations.py` from the code template on the Wiki, implement the function _group_by_ for grouping rows of a table and aggregating columns within each group.

In `queries.py` you find a function _run_group_by_sequence_ that runs a sequence of operations for
the query

_Top 10 directors by average IMDb score with at least 10 movies, considering only movies with at
least 100,000 votes._

Find a better sequence of operations for this query and enter it into _run_improved_group_by_sequence_.
You can compare the runtimes of the two sequences by calling `python queries.py *.tsv --exercise
2`. Explain how your changes improve the runtime in `experiences.md`.

## Exercise 3
In `queries.sql`, write down the SQL query that answers the following question:

_What are the movies with the highest IMDb score for each decade, considering only movies with
at least 500,000 votes?_

The output of your query should match the one given in `queries.sql`.

## Feedback

As usual, in your `experiences.md`, provide a brief account of your experience with this sheet and
the corresponding lecture. Make sure to add a statement asking for feedback. In this statement
specify to which degree and on which parts of the sheet you want feedback. In addition, say how
much time you invested and if you had major problems, and if yes, where.

This ends our three lectures on relational databases and SQL, we hope you enjoyed it.
