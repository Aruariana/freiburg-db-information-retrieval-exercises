"""
Copyright 2023, University of Freiburg
Chair of Algorithms and Data Structures

Elmar Haussmann <haussmann@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
Natalie Prange <prange@cs.uni-freiburg.de>
Sebastian Walter <swalter@cs.uni-freiburg.de>
"""
import argparse
import re

import torch

WORD_PATTERN = re.compile(r"\b\w+(['-]\w+)*\b")


def tokenize(s: str) -> list[str]:
    """

    Splits a string into tokens.

    >>> tokenize("This   is a sentence.")
    ['This', 'is', 'a', 'sentence']
    """
    return list(match.group() for match in WORD_PATTERN.finditer(s))


def compute_vocabulary(file: str) -> dict[str, int]:
    """

    Reads the given file and generates vocabulary mapping
    from word to word id.

    """
    # map from word to id
    word_vocab: dict[str, int] = {}

    # read the file (containing the training data).
    word_id = 0
    with open(file, "r", encoding="utf8") as f:
        for line in f:
            _, text = line.strip().split("\t")

            # add the words to the vocabulary.
            for word in tokenize(text):
                if word in word_vocab:
                    continue
                word_vocab[word] = word_id
                word_id += 1

    return word_vocab


def read_labeled_data(
    file: str,
    word_vocab: dict[str, int],
    word_embeddings: dict[str, torch.Tensor] | None = None
) -> tuple[torch.Tensor, torch.Tensor]:
    """

    Reads the given tab-separated file where each line
    contains a label, either 0 or 1, in the first column
    and a text document in the second column,
    and returns a matrix containing document representations
    and a label vector.

    If no word embeddings are specified, a document's
    representation should be a word frequency vector (sum of all
    one-hot word representations) using the given
    word vocabulary. To avoid memory issues in this case, use
    a sparse matrix to store the vectors.

    If word embeddings are specified, a document's representation
    should be the sum of all word representations (ignoring words
    for which no embedding exists).

    >>> import torch
    >>> torch.set_printoptions(precision=3)
    >>> embs = torch.load("example.pt")
    >>> v = compute_vocabulary("example.train.tsv")
    >>> X, y = read_labeled_data("example.train.tsv", v)
    >>> X.is_sparse
    True
    >>> X.to_dense()
    tensor([[2., 1.],
            [5., 2.],
            [3., 5.],
            [3., 2.],
            [1., 3.],
            [2., 4.],
            [1., 3.]])
    >>> y  # the vector of labels
    tensor([0, 0, 1, 0, 1, 1, 1])
    >>> X, y = read_labeled_data("example.train.tsv", v, embs)
    >>> X
    tensor([[ 0.000,  2.500],
            [ 0.500,  6.000],
            [-3.500,  5.500],
            [-0.500,  4.000],
            [-2.500,  2.500],
            [-3.000,  4.000],
            [-2.500,  2.500]])
    >>> y  # the vector of labels
    tensor([0, 0, 1, 0, 1, 1, 1])
    """
    labels = []
    texts = []
    with open(file, "r", encoding="utf8") as f:
        for i, line in enumerate(f):
            label, text = line.rstrip("\r\n").split("\t")
            labels.append(int(label))
            texts.append(text)

    if word_embeddings is not None:
        assert len(word_embeddings) > 0, \
            "got empty word embeddings"
        X = []
        for text in texts:
            embeddings = []
            for word in tokenize(text):
                if word not in word_embeddings:
                    continue
                embeddings.append(word_embeddings[word])

            if len(embeddings) == 0:
                embedding = torch.zeros_like(
                    next(iter(word_embeddings.values()))
                )
            else:
                embedding = torch.stack(embeddings).sum(0)

            X.append(embedding)

        X = torch.stack(X)

    else:
        rows = []
        cols = []
        values = []

        for i, text in enumerate(texts):
            for word in tokenize(text):
                if word not in word_vocab:
                    continue
                rows.append(i)
                cols.append(word_vocab[word])
                # duplicate values at the same position i,j are summed
                values.append(1.0)

        X = torch.sparse_coo_tensor(
            torch.tensor([rows, cols]),
            torch.tensor(values),
            size=(len(texts), len(word_vocab)),
            dtype=torch.float,
        )

    y = torch.tensor(labels, dtype=torch.long)
    return X, y


class LogisticRegression:
    def __init__(self, num_features: int) -> None:
        """

        Sets up the logistic regression model.

        """
        # add one dimension for bias
        self.num_features = 1 + num_features

        # weights stores the normal vector of the separating hyperplane
        # we begin with w = (0, ...., 0)
        self.weights = torch.zeros(
            self.num_features,
            dtype=torch.float
        )

    def add_bias(self, X: torch.Tensor) -> torch.Tensor:
        """

        Adds ones for the bias to the given input matrix X.

        >>> import torch
        >>> lr = LogisticRegression(0)
        >>> t = torch.tensor([[1.0, 2.0], [3.0, 4.0]], dtype=torch.float)
        >>> lr.add_bias(t)
        tensor([[1., 1., 2.],
                [1., 3., 4.]])
        """
        # this only works with dense matrices in torch,
        # so make sure to call it on batches only and not
        # the whole dataset
        assert X.ndim == 2, "X must be a matrix"
        ones = torch.ones((X.shape[0], 1), dtype=X.dtype)
        return torch.cat([ones, X.to_dense()], dim=1)

    def train(
        self,
        X: torch.Tensor,
        y: torch.Tensor,
        epochs: int = 10,
        learning_rate: float = 0.1,
        batch_size: int = 32,
        verbose: bool = False
    ) -> None:
        """

        Trains a logistic regression model on inputs X and
        associated labels y.

        Training should be done in batches of size batch_size for the
        given number of epochs, as explained in the lecture.

        >>> import torch
        >>> torch.set_printoptions(precision=3)
        >>> v = compute_vocabulary("example.train.tsv")
        >>> X, y = read_labeled_data("example.train.tsv", v)
        >>> lr = LogisticRegression(len(v))
        >>> lr.train(X, y, epochs=1, learning_rate=1, batch_size=1)
        >>> lr.weights
        tensor([-0.498, -1.008,  2.503])
        >>> lr = LogisticRegression(len(v))
        >>> lr.train(X, y, epochs=1, learning_rate=1, batch_size=10)
        >>> lr.weights
        tensor([ 0.071, -0.214,  0.714])
        >>> lr = LogisticRegression(len(v))
        >>> lr.train(X, y, epochs=10, learning_rate=0.1, batch_size=10)
        >>> lr.weights
        tensor([-0.001, -0.321,  0.419])
        """

        # iterate over all epochs
        for epoch in range(epochs):
            if verbose:
                print(f"Epoch {epoch + 1}...")

            # iterate over the training set
            for i in range(0, len(X), batch_size):
                # get batch from inputs and labels
                indices = torch.arange(i, min(len(X), i + batch_size))
                X_b = torch.index_select(X, 0, indices)
                y_b = y[i:i+batch_size]

                # add ones for the biases
                X_b = self.add_bias(X_b)

                # run logistic regression with current weights
                outputs = torch.sigmoid(torch.matmul(self.weights, X_b.T))

                # update the normal vector / weights
                gradient = torch.matmul(X_b.T, (y_b - outputs).T) / len(X_b)
                self.weights += learning_rate * gradient

    def predict(
        self,
        X: torch.Tensor,
        batch_size: int = 32
    ) -> torch.Tensor:
        """

        Predicts a label for each row in the input X
        based on the learned weights. Implement in a batched fashion
        to avoid memory issues.

        >>> v = compute_vocabulary("example.train.tsv")
        >>> X, y = read_labeled_data("example.train.tsv", v)
        >>> lr = LogisticRegression(len(v))
        >>> lr.train(X, y, epochs=10, learning_rate=0.1, batch_size=10)
        >>> X_test, y_test = read_labeled_data("example.test.tsv", v)
        >>> lr.predict(X_test)
        tensor([0, 1, 0])
        >>> lr.predict(X)
        tensor([0, 0, 1, 0, 1, 1, 1])
        """
        labels = []

        # predict in batched fashion
        for i in range(0, len(X), batch_size):
            indices = torch.arange(i, min(len(X), i + batch_size))
            X_b = torch.index_select(X, 0, indices)
            X_b = self.add_bias(X_b)

            # compute outputs without sigmoid
            outputs = torch.matmul(self.weights, X_b.T)

            # sigmoid >= 0.5 if outputs >= 0
            predictions = torch.where(outputs >= 0., 1, 0)
            labels.append(predictions)

        return torch.cat(labels)

    def evaluate(
        self,
        X: torch.Tensor,
        y: torch.Tensor
    ) -> tuple[float, float, float]:
        """

        Predict classes for inputs X and calculate
        precision, recall and f1-score.

        >>> v = compute_vocabulary("example.train.tsv")
        >>> X_train, y_train = read_labeled_data("example.train.tsv", v)
        >>> X_test, y_test = read_labeled_data("example.test.tsv", v)
        >>> lr = LogisticRegression(len(v))
        >>> lr.train(X_train, y_train)
        >>> precision, recall, f1 = lr.evaluate(X_test, y_test)
        >>> precision
        1.0
        >>> recall
        0.5
        >>> round(f1, 2)
        0.67
        """
        # predict the classes for the data
        predictions = self.predict(X)

        n_corr = (predictions * y).sum().item()
        # with no true positives, all three measures are zero
        if n_corr == 0:
            return 0, 0, 0

        n_pred = predictions.sum().item()
        n_total = y.sum().item()

        recall = n_corr / n_total
        precision = n_corr / n_pred
        f1 = (2 * precision * recall) / (precision + recall)
        return precision, recall, f1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("train_data", type=str, help="path to the train data")
    parser.add_argument("test_data", type=str, help="path to the test data")
    parser.add_argument(
        "-emb",
        "--embeddings",
        type=str,
        default=None,
        help="path to word embeddings file"
    )
    parser.add_argument(
        "-lr",
        "--learning-rate",
        type=float,
        default=0.1,
        help="learning rate for training"
    )
    parser.add_argument(
        "-b",
        "--batch-size",
        type=int,
        default=32,
        help="batch size for training"
    )
    parser.add_argument(
        "-e",
        "--epochs",
        type=int,
        default=10,
        help="number of epochs for training"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print additional information during training"
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    """

    Trains a logistic regression model on the given training data and evaluates
    it on the given test data. Prints the precision, recall and f1-score.

    """
    torch.manual_seed(2324)
    torch.use_deterministic_algorithms(True)

    # get vocabulary, optional embeddings and data
    word_vocab = compute_vocabulary(args.train_data)
    if args.embeddings is not None:
        word_embeddings = torch.load(args.embeddings)
    else:
        word_embeddings = None

    X_train, y_train = read_labeled_data(
        args.train_data,
        word_vocab,
        word_embeddings
    )
    X_test, y_test = read_labeled_data(
        args.test_data,
        word_vocab,
        word_embeddings
    )

    # setup the model
    _, num_features = X_train.shape
    lr = LogisticRegression(num_features)

    # train the model
    lr.train(
        X_train,
        y_train,
        args.epochs,
        args.learning_rate,
        args.batch_size,
        args.verbose
    )

    # evaluate the model
    precision, recall, f1 = lr.evaluate(X_test, y_test)

    print(f"\nPrecision: {precision:.2%}")
    print(f"Recall:    {recall:.2%}")
    print(f"F1-score:   {f1:.2%}")


if __name__ == "__main__":
    main(parse_args())
