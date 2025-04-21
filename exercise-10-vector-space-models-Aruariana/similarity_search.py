import argparse
import time
# import readline  # noqa
import re

# we use the Python implementation in qgram_index.py
# here because we need to access the infos attribute
# of the QGramIndex class, which is not available
# in the Rust implementation; also speed is not
# an issue this time, because we only search through
# ~110k movie titles
from qgram_index import QGramIndex  # type: ignore

import torch


WORD_PATTERN = re.compile(r"\b\w+(['-]\w+)*\b")


def tokenize(s: str) -> list[str]:
    """

    Splits a string into tokens.

    >>> tokenize("This   is a sentence.")
    ['This', 'is', 'a', 'sentence']
    """
    return list(match.group() for match in WORD_PATTERN.finditer(s))


class EmbeddingIndex:
    """

    A simple embedding index for similarity search.

    """

    def __init__(self) -> None:
        """

        Initialize the embedding index.

        """
        # map from token to its embedding
        self.token_embeddings: dict[str, torch.Tensor] = {}
        self.length_embeddings = 0

        # matrix of shape [#documents, D] containing all document embedding
        self.document_embeddings: torch.Tensor = torch.empty(
            (0, 0),
            dtype=torch.float
        )



    def load_embeddings(self, file: str) -> None:
        """

        Loads the token embeddings from a file.

        """
        self.token_embeddings = torch.load(file)
        self.length_embeddings = next(iter(self.token_embeddings.values())).shape[0]

    def build_from_documents(self, documents: list[str]) -> None:
        """

        Builds and stores the embeddings of the given documents.

        """
        self.document_embeddings = torch.stack([
            self.embed_document(document)
            for document in documents
        ])

    def embed_document(self, document: str) -> torch.Tensor:
        """

        Calculates an embedding of a document by splitting
        it into tokens and summing the token representations.
        Out of vocabulary tokens should be treated as all zero vectors.
        Use the given tokenize function for splitting a text into tokens.

        >>> import torch
        >>> torch.set_printoptions(precision=1)
        >>> idx = EmbeddingIndex()
        >>> idx.token_embeddings = {
        ...    "a": torch.tensor([1.0, 0.5]),
        ...    "b": torch.tensor([-2.0, 1.5])
        ... }
        >>> idx.embed_document("")
        tensor([0., 0.])
        >>> idx.embed_document("a b a")
        tensor([0.0, 2.5])
        >>> idx.embed_document("b b")
        tensor([-4.,  3.])
        """
        assert len(self.token_embeddings) > 0, \
            "empty token embeddings, load them before embedding documents"

        # TODO: add your code here
        if self.length_embeddings == 0:
            self.length_embeddings = next(iter(self.token_embeddings.values())).shape[0]
        embedded_doc = torch.zeros(self.length_embeddings)
        for token in tokenize(document):
            if token in self.token_embeddings:
                embedded_doc += self.token_embeddings[token]


        return embedded_doc


    def cosine_similarity(
        self,
        v: torch.Tensor,
        m: torch.Tensor
    ) -> torch.Tensor:
        """

        Computes the cosine similarity between a vector v of shape [D]
        and all rows of a matrix m with shape [N, D],
        returning a vector of shape [N] containing the similarities.

        >>> import torch
        >>> torch.set_printoptions(precision=3)
        >>> idx = EmbeddingIndex()
        >>> m = torch.tensor([[10.0, 0.0], [0.0, 0.1], \
                              [8.0, 8.0], [-4.5, 0.0]])
        >>> idx.cosine_similarity(torch.tensor([4.0, 0.0]), m)
        tensor([ 1.000,  0.000,  0.707, -1.000])
        >>> idx.cosine_similarity(torch.tensor([0.0, 0.0]), m)
        tensor([0., 0., 0., 0.])
        """
        assert v.ndim == 1 and m.ndim == 2, \
            "v must be a vector and m must be a matrix"

        # TODO: add your code here

        v_norm = torch.norm(v)
        m_norms = torch.norm(m, dim=1, keepdim=True)

        v_normalized = v / v_norm
        m_normalized = m / m_norms

        result = m_normalized @ v_normalized
        result = result.nan_to_num()

        return result

    def top_k_neighbors(
        self,
        document: str,
        k: int
    ) -> list[tuple[int, float]]:
        """

        Returns the zero-based indices and distances of the top k most similar
        documents from the index for the given document by cosine similarity.

        >>> idx = EmbeddingIndex()
        >>> idx.token_embeddings = {
        ...    "a": torch.tensor([1.0, 0.5]),
        ...    "b": torch.tensor([-2.0, 1.5])
        ... }
        >>> idx.build_from_documents(["a a a b", "b b", "a b", ""])
        >>> [(i, round(s, 3)) for i, s in idx.top_k_neighbors("a a a b", 2)]
        [(0, 1.0), (2, 0.707)]
        >>> [(i, round(s, 3)) for i, s in idx.top_k_neighbors("b", 2)]
        [(1, 1.0), (2, 0.894)]
        >>> idx.top_k_neighbors("b", 0)
        []
        """
        assert len(self.document_embeddings) > 0, \
            "empty document embeddings, build them before searching"

        # TODO: add your code here

        embedded_doc = self.embed_document(document)
        result_tensor = self.cosine_similarity(embedded_doc, self.document_embeddings)
        result_list = result_tensor.tolist()
        result_list = [(i, sim) for i, sim in enumerate(result_list)]
        result_list.sort(key=lambda x: x[1], reverse=True)
        return result_list[:k]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "movies",
        type=str,
        help="path to movies file for q-gram index"
    )
    parser.add_argument(
        "embeddings",
        type=str,
        help="path to the word embeddings"
    )
    parser.add_argument(
        "-q",
        "--q-grams",
        type=int,
        default=3,
        help="size of the q-grams"
    )
    parser.add_argument(
        "-k",
        "--top-k",
        type=int,
        default=5,
        help="size of the top k"
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    """

    Builds a qgram index from the given file and then, in an infinite loop,
    lets the user search for a movie and displays the movie itself and its
    top k most similar movies.

    """
    # Create a new index from the given file.
    print(f"Building q-gram index from file {args.movies}.")
    start = time.perf_counter()
    q = QGramIndex(args.q_grams)
    q.build_from_file(args.movies)
    print(f"Done, took {(time.perf_counter() - start) * 1000:.1f}ms.")

    s = EmbeddingIndex()
    start = time.perf_counter()
    print(f"Loading word embeddings from file {args.embeddings}.")
    s.load_embeddings(args.embeddings)
    print(f"Done, took {(time.perf_counter() - start) * 1000:.1f}ms.")
    start = time.perf_counter()
    print("Computing plot embeddings for movies in q-gram index.")
    s.build_from_documents([infos[1] for *_, infos in q.infos])
    print(f"Done, took {time.perf_counter() - start:.1f}s.")

    while True:
        # Ask the user for a keyword query.
        query = input("\nYour keyword query: ")
        query = q.normalize(query)
        if len(query) == 0:
            print("Query must not be empty.")
            continue

        start = time.perf_counter()

        # Process the keywords.
        delta = len(query) // (args.q_grams + 1)

        postings = q.find_matches(query, delta)
        num_results = min(5, len(postings))
        if num_results == 0:
            print("No matching movies found.")
            continue

        print(f"\nFound {num_results} matching movies:")

        names = []
        plots = []
        for i, (id, _) in enumerate(postings[:num_results]):
            info = q.get_infos(id)
            assert info is not None, "invalid ID"
            _, name, score, infos = info
            plot = infos[1]
            year = infos[0]
            print(f"  {i+1}. {name} ({year} | {score:,} votes)")
            names.append(name)
            plots.append(plot)

        selection = input("\nSelect a movie: ")
        if not selection.isdigit():
            continue

        index = int(selection)
        if index < 1 or index > num_results:
            print("Invalid selection.")
            continue

        # TODO: add your code here
        similar_movies = s.top_k_neighbors(names[index - 1] + plots[index - 1], args.top_k)
        for i, movie in enumerate(similar_movies):
            id, sim_score = movie
            movie_info = q.get_infos(id+1)
            assert movie_info is not None, "invalid ID"
            _, name, score, infos = movie_info
            year = infos[0]
            print(f"  {i + 1}. {name} ({year} | {score:,} votes) | similarity: {sim_score}")



if __name__ == "__main__":
    main(parse_args())
 