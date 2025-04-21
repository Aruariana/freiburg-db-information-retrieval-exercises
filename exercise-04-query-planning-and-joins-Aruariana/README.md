[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Prjbv0C1)
# Data Bases and Information Systems - Exercise Sheet 4 
Prof. Dr. Joschka Bödecker, Julien Brosseit, Daniel Jost

![introduction image](./images/main.png)


Exercise developed by **Prof. Dr. Hannah Bast and Team** with slight modifications  
Submit until **Wednesday, 27 November 2024**

## Exercise 1

Extend `operations.py` from the code template as detailed in the following.
1. Implement the function `project` for selecting columns from a table.
2. Implement the function `select` for selecting rows from a table.
3. Implement the function `join` for joining two tables on one column. The join should be a hash-based equi-join as described in the lecture.

## Exercise 2

First, download the TSV files containing the table data [here](http://ad-teaching.informatik.uni-freiburg.de/InformationRetrievalWS2324/datasets/movies-tables.tar.gz) and extract it in the current folder. Then, for the following query, determine three different sequences of operations (each operation in {`projection`, `selection`, `join`}) that all return the same result:

*Actors who won a Golden Globe for a movie with an IMDb score of 8.0 or higher since 2010, including the name of the movie, the role played, and the type of Golden Globe award.*

Enter your sequences of operations as code into `queries.py` using your implementations from exercise 1. You can and should look at the corresponding SQL statement in `queries.sql` for guidance.
We also provide an example for a different query and SQL statement in `queries.py` which can be executed using `python3 queries.py *.tsv --example`, assuming you downloaded the TSV files to the same directory.
Verify the correctness of your results by executing `python3 queries.py *.tsv` and comparing its output to the one of SQLite3. Execute `cat queries.sql | sqlite3` to get the SQLite3 output.
Enter the runtimes of your three sequences of operations and the runtime of SQLite3 with and without indices into the table in the `experiences.md`, following the format of the rows already there.

As usual, in your `experiences.md`, provide a brief account of your experience with this sheet and the corresponding lecture. Make sure to add a statement asking for feedback. In this statement specify to which degree and on which parts of the sheet you want feedback. In addition, say how much time you invested and if you had major problems, and if yes, where.
