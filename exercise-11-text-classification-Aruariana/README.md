[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/96z94h97)
# Data Bases and Information Systems - Exercise Sheet 11
Prof. Dr. Joschka Bödecker, Julien Brosseit, Daniel Jost

![header image](./images/main.png)

Exercise developed by **Prof. Dr. Hannah Bast and Team** with slight modifications  
Submit until **Wednesday, 5 February 2025**

This exercise sheet is about text classification using logistic regression. The task is to predict
whether a movie is a comedy or not given its plot description. You should implement the training
and prediction with linear algebra using PyTorch.

## Exercise 1

Extend `logistic_regression.py` by the following functionality:

1. Write a method `train` that learns the logistic regression weight vector for a given set of training
documents with labels. Your method should train on batches of documents over multiple epochs,
as explained in the lecture.
_Hint: Use torch.index select for selecting rows by index from a sparse or dense matrix in PyTorch._
2. Write a method `predict` that predicts a class for each document from a given test set, using the
logistic regression weight vector learned during training.
3. Write a method `evaluate` that calculates precision, recall, and F1-score for a given test set.
4. Train and evaluate a logistic regression model on the data provided. By default,
the input to the model will be a document vector with term frequencies (tf scores) built from
the movie plot description. Experiment with the following hyperparameters: the learning rate,
the number of epochs and the batch size. Enter the precision, recall and F1-score for the best
combination of hyperparameters into the table in `experiences.md`.
_Hint: Training will take a little longer for this task because of the high number of input dimensions._
5. Do the same as in task 4, but this time with document embeddings as input to the logistic
regression model. For that, download both the `fastText` and `random` word embeddings from our [ILIAS](https://ilias.uni-freiburg.de/goto.php?target=fold_3757917&client_id=unifreiburg). You can pass them to the script with the `--embeddings` option. Then the input vector to the
model for a given document will be the sum of the embeddings of the contained words. Again,
enter precision, recall and F1-score for the best combination of hyperparameters for both types
of embeddings into the table linked on the Wiki.
6. Briefly document your findings from tasks 4 and 5 in your `experiences.md`.

As usual, in your `experiences.md`, provide a brief account of your experience with this sheet and
the corresponding lecture. Make sure to add a statement asking for feedback. In this statement
specify to which degree and on which parts of the sheet you want feedback. In addition, say how
much time you invested and if you had major problems, and if yes, where.
