[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/KI0xviYu)
# Data Bases and Information Systems - Exercise Sheet 10
Prof. Dr. Joschka Bödecker, Julien Brosseit, Daniel Jost

![header image](./images/main.png)

Exercise developed by **Prof. Dr. Hannah Bast and Team** with slight modifications  
Submit until **Wednesday, 29 January 2025**


## Exercise 1
This exercise is about implementing the inverted index from exercise sheet 2 with linear algebra. Extend `inverted_index.py` from the code template by the following functionality. 
1. Implement the method `build_td_matrix` that builds the term-document matrix from the inverted index using BM25 scores as entries. 
2. Implement the method `process_query` such that the result list is obtained via a multiplication of the term-document matrix with the query vector (and not via merging of the inverted lists, like in exercise sheet 2).
3. Make sure that your inverted index gives the exact same results as the one from exercise sheet 2 by trying out a few example queries. You can use your own solution or the master solution for exercise sheet 2 for that. 
   
*Note:* You can use the code from the lecture as an orientation. The only differences are that you should use BM25 scores, whereas in the lecture we used simple tf scores, and that you should use sparse matrices, because it would be too slow (and too space consuming) otherwise.

## Exercise 2
This exercise is about implementing a simple similarity search engine for text documents. Extend `similarity_search.py` from the code template by the following functionality.
1. Implement the method `embed_document` that computes the embedding of a document as the sum of the embeddings of its words.
2. Implement the method `cosine_similarity` that computes the cosine similarity between a vector and all rows of a matrix.
3. Implement the method `top_k_neighbors` that for a given document returns the *k* most similar documents by cosine similarity, sorted in descending order.
4. Complete the `main` method, such that for a given document the top *k* most similar documents and the document itself are displayed together with their cosine similarity. In our case, the documents will be movie plots (also see the next item).
5. Download the file `movies-plots.tsv` from ILIAS and run the similarity search for the movies *”Interstellar”*, *”Inception”*, *”Harry Potter and the Sorcerer’s Stone”*, and *”Saving Private Ryan”*, both with the *fastText* and *random word embeddings* provided here. Compare the results and write a short paragraph in your `experiences.md` about your findings.


As usual, in your `experiences.md`, provide a brief account of your experience with this sheet and the corresponding lecture. Make sure to add a statement asking for feedback. In this statement specify to which degree and on which parts of the sheet you want feedback. In addition, say how much time you invested and if you had major problems, and if yes, where.