I want feedback on my results and implementation on Exercise 1 because I'm not quite sure why the estimation and 
real results don't match.


Exercise 1

Cost of sequence 1: 310,774.0

Cost of sequence 2: 888,305.0

Cost ratio: 0.35

Sequence 1 took 36.7ms

Sequence 2 took 30.7ms

Runtime ratio: 1.20

I took two approaches, joining them first then selecting (seq1) and selecting them first then joining (seq2).

In the estimation of costs, sequence 1 is cheaper than sequence 2. But in the findings, it turns out that sequence 1 is 
slower than sequence 2. I think this is because of the estimation of selection. We estimate that selection selects half
of the rows. But the selections we do in this example seems to be selecting quite less than half. Also selection is 
estimated to be n*k, but in this example we only use one value from one row, it should be n. The biggest table here is by
far the movies table. So if we select from the movies first, it shows us a great cost. And if we join it first, it 
estimates the rows will be min of the two tables. So the first table that is the result of the first join will have much
less rows, which is the contributing factor why the first one's estimated cost is lesser. In reality, it seems that 
selecting first lowers the rows far more, leading to a faster time (seq2).

Exercise 2

Sequence took 399.3ms
Improved sequence took 381.9ms
Runtime ratio: 1.05

I could only improve by a small amount by pushing the join with persons table further to the plan. Persons table is not
needed until the end where you need the name of the director.

Exercise 3

I couldn't write the query by myself after trying more than one hour. At the end I got a solution from chatgpt and
understand it. It was hard for me.
