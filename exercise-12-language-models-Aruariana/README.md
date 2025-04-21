[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/bLULtHgo)
# Data Bases and Information Systems - Exercise Sheet 12
Prof. Dr. Joschka Bödecker, Julien Brosseit, Daniel Jost

![header image](./images/main.png)

Exercise developed by **Prof. Dr. Hannah Bast and Team** with slight modifications  
Submit until **Wednesday, 12 February 2025**

This exercise sheet is about training and running a simple next-token model.

## Exercise 1

1. In `model.py` finish the implementation of the NextTokenModel class. This was demonstrated and explained in the lecture.
2. In `model.py` implement the function sample next token which returns the next token given a distribution over a vocabulary. Determine the next token by sampling from the normalized distribution over the k tokens with the highest probabilities.
3. In `train.py` implement the epoch training loop. It is recommended to also add functionality to print some statistics during training like the training time or current training loss, so that you are able to follow the training progress. Hint: While implementing the training functionality it is advisable to compile a small dummy dataset that is easy to learn, so that you can test whether your implementation works (e.g., predicting the next letter in the alphabet).
4. Train a next-token model on the training data given in ILIAS with the `train.py` script. The data is a single text file containing the transcripts of the lectures from the last course and the predecessor course in the WS 22/23. Experiment with hyperparameters, most importantly the tokenizer, context length, learning rate, batch size, and hidden dimensionality (the d from Lecture 12, slide 20). If you have a GPU on your machine, you can speed up training by specifying the `--device` cuda option. You can save the trained model in a file with the `--checkpoint` option such that you are able to use it later for inference (see the next task). Hint: If you only have a CPU, training might take a couple of minutes.
5. Run your models from the previous task using the `test.py` script. Again, you can specify which model to use with the `--checkpoint` option. Play around with different input prefixes and different values of k for your sample next token function from task 2.
6. Report your findings from task 4 and 5 in your `experiences.md`. Specify at least 3 interesting model outputs and for each of them a short description of the model and hyperparameters you used to obtain it.
7. (Optional) Build your own training dataset in form of a single or multiple text files. This can be whatever you find interesting, e.g., a collection of SQL queries, German tweets, or Python code. Repeat tasks 4 to 6 for this dataset. Make sure that your dataset in total is smaller than 1 MB and also commit it to the Repository.


As usual, in your `experiences.md`, provide a brief account of your experience with this sheet and the corresponding lecture. Make sure to add a statement asking for feedback. In this statement specify to which degree and on which parts of the sheet you want feedback. In addition, say how much time you invested and if you had major problems, and if yes, where.