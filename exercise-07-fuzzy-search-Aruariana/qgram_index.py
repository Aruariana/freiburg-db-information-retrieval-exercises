"""
Copyright 2019, University of Freiburg
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
Natalie Prange <prange@cs.uni-freiburg.de>
Sebastian Walter <swalter@cs.uni-freiburg.de>
"""
import math
# import readline  # noqa
import re
import argparse
import time


try:
    # try to import the ad_freiburg_qgram_utils package,
    # which contains faster Rust-based implementations of the ped and
    # merge_lists functions; install it via pip install ad-freiburg-qgram-utils
    from ad_freiburg_qgram_utils import (  # type: ignore
        ped,  # type: ignore
        sort_merge as merge_lists,  # type: ignore
    )
except ImportError:
    # fallback to the Python implementation in utils.py
    # if the ad_freiburg_qgram_utils is not installed
    from utils import ped, merge_lists


class QGramIndex:
    """

    A QGram-Index.

    """

    def __init__(self, q: int, use_syns: bool = False):
        """

        Creates an empty qgram index.

        """
        assert q > 0, "q must be greater than zero"
        self.q = q
        self.use_syns = use_syns
        self.padding = "$" * (self.q - 1)
        # map from q-gram to list of (ID, frequency) tuples
        self.inverted_lists: dict[str, list[tuple[int, int]]] = {}

        self.entities: dict[int, list[str]] = {}

        self.num_of_inverted_lists_merged = 0

        # statistics for doctests and output, calculated in
        # find_matches

        # tuple of (
        #   number of actual PED computations,
        #   number of potential PED computations / length of merged list
        # )
        self.ped_stats = (0, 0)

    def build_from_file(self, file_name: str) -> None:
        """

        Builds the index from the given file.

        The file should contain one entity per line, in the following format:
            name\tscore\tsynonyms\tinfo1\tinfo2\t...

        Synonyms are separated by a semicolon.

        An example line:
            Albert Einstein\t275\tEinstein;A. Einstein\tGerman physicist\t..."

        The entity IDs are one-based (starting with one).

        >>> q = QGramIndex(3, False)
        >>> q.build_from_file("test.tsv")
        >>> sorted(q.inverted_lists.items())
        ... # doctest: +NORMALIZE_WHITESPACE
        [('$$b', [(2, 1)]), ('$$f', [(1, 1)]), ('$br', [(2, 1)]),
         ('$fr', [(1, 1)]), ('bre', [(2, 1)]), ('fre', [(1, 1)]),
         ('rei', [(1, 1), (2, 1)])]
        """
        # TODO: build the q-gram index

        with open(file_name, "r", encoding='utf8') as file:
            for index, line in enumerate(file):
                if index == 0:
                    continue

                line = line.strip()
                elements = line.split("\t")
                self.entities[index] = elements

                word = elements[0]

                qgrams = self.compute_qgrams(self.normalize(word))

                for qgram in qgrams:
                    if qgram not in self.inverted_lists:
                        self.inverted_lists[qgram] = [(index, 1)]
                    else:
                        if self.inverted_lists[qgram][-1][0] != index:
                            self.inverted_lists[qgram].append((index, 1))
                        else:
                            self.inverted_lists[qgram][-1] = (index, self.inverted_lists[qgram][-1][1]+1)



    def compute_qgrams(self, word: str) -> list[str]:
        """

        Compute q-grams for padded version of given string.

        >>> q = QGramIndex(3, False)
        >>> q.compute_qgrams("freiburg")
        ['$$f', '$fr', 'fre', 'rei', 'eib', 'ibu', 'bur', 'urg']
        >>> q.compute_qgrams("f")
        ['$$f']
        >>> q.compute_qgrams("")
        []
        """
        # TODO: compute the q-grams

        word = self.padding + word

        return [word[i:i+self.q] for i in range(len(word) - self.q + 1)]

    def find_matches(
        self,
        prefix: str,
        delta: int
    ) -> list[tuple[int, int]]:
        """

        Finds all entities y with PED(x, y) <= delta for a given integer delta
        and a given prefix x. The prefix should be normalized and non-empty.
        You can assume that the threshold for filtering PED computations
        (defined below) is greater than zero. That way, it suffices to only
        consider names which have at least one q-gram in common with prefix.

        Returns a list of (ID, PED) tuples ordered first by PED and then entity
        score. The IDs are one-based (starting with 1).

        Also calculates statistics about the PED computations and saves them in
        the attribute ped_stats.

        >>> q = QGramIndex(3, False)
        >>> q.build_from_file("test.tsv")
        >>> q.find_matches("frei", 0)
        [(1, 0)]
        >>> q.ped_stats
        (1, 2)
        >>> q.find_matches("frei", 1)
        [(1, 0), (2, 1)]
        >>> q.ped_stats
        (2, 2)
        >>> q.find_matches("freib", 1)
        [(1, 1)]
        >>> q.ped_stats
        (1, 2)
        """
        assert len(prefix) > 0, "prefix must not be empty"
        threshold = len(prefix) - (self.q * delta)
        assert threshold > 0, \
            "threshold must be positive, adjust delta accordingly"

        # TODO: compute and sort the matches, the algorithm and advice
        # was given in the lecture

        # prefix = self.normalize(prefix)
        qgrams = self.compute_qgrams(prefix)

        qgram_index = []
        for qgram in qgrams:
            if qgram in self.inverted_lists:
                qgram_index.append(self.inverted_lists[qgram])
        self.num_of_inverted_lists_merged = len(qgram_index)

        intersection_list = merge_lists(qgram_index)
        num_of_potential_ped = len(intersection_list)

        possible_match_ids = [element[0] for element in intersection_list if element[1] >= threshold]
        num_of_ped = len(possible_match_ids)

        self.ped_stats = (num_of_ped, num_of_potential_ped)

        ped_values = []
        for id in possible_match_ids:
            ped_value = ped(prefix, self.normalize(self.entities[id][0]), delta)
            if ped_value <= delta:
                ped_values.append((id, ped_value))

        ped_values = sorted(ped_values, key=lambda x: (x[1], -int(self.entities[x[0]][1])))

        return ped_values


    def get_infos(
        self,
        id: int
    ) -> tuple[str, str, int, list[str]] | None:
        """

        Returns the synonym, name, score and additional info for the given ID.
        If the index was built without synonyms, the synonym is always
        equal to the name. Returns None if the ID is invalid.

        >>> q = QGramIndex(3, False)
        >>> q.build_from_file("test.tsv")
        >>> q.get_infos(1)
        ('frei', 'frei', 3, ['first entity', 'used for doctests'])
        >>> q.get_infos(2)
        ('brei', 'brei', 2, ['second entity', 'also for doctests'])
        >>> q.get_infos(3)
        """
        # TODO: return infos for the given ID

        if id not in self.entities:
            return None

        return self.entities[id][0], self.entities[id][0], int(self.entities[id][1]), [item for item in self.entities[id][3:]]


    def normalize(self, word: str) -> str:
        """

        Normalize the given string (remove non-word characters and lower case).

        >>> q = QGramIndex(3, False)
        >>> q.normalize("freiburg")
        'freiburg'
        >>> q.normalize("Frei, burG !?!")
        'freiburg'
        >>> q.normalize("Frei14burg")
        'frei14burg'
        """
        return "".join(m.group(0).lower() for m in re.finditer(r"\w+", word))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        type=str,
        help="file to build q-gram index from"
    )
    parser.add_argument(
        "-q",
        "--q-grams",
        type=int,
        default=3,
        help="size of the q-grams"
    )
    parser.add_argument(
        "-s",
        "--use-synonyms",
        action="store_true",
        help="whether to use synonyms for the q-gram index"
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    """

    Builds a qgram index from the given file and then, in an infinite loop,
    lets the user type a query and shows the result for the normalized query.

    """
    # TODO: add your code

    qgram_index = QGramIndex(args.q_grams, args.use_synonyms)
    qgram_index.build_from_file(args.file)

    while True:

        query = qgram_index.normalize(input("Query: "))
        if query == "":
            break
        start_time = time.perf_counter()
        delta = int(len(query) / (qgram_index.q+1))
        results = qgram_index.find_matches(query, delta)
        end_time = time.perf_counter()

        query_time = end_time - start_time
        print(f"The query took {query_time:.6f} seconds")
        print(f"Number of inverted lists that were merged: {qgram_index.num_of_inverted_lists_merged}")
        print(f"Number of potential PED computations: {qgram_index.ped_stats[1]}")
        print(f"Number of PED computations: {qgram_index.ped_stats[0]}")

        if len(results) > 5:
            print(f"\nFound {len(results)} matches for {query}\nShowing Top 5 results:")

        for index, result in enumerate(results[:5]):
            print()
            info = qgram_index.get_infos(result[0])
            word = info[1]
            description = info[3][1]
            wikidata_url = "https://www.wikidata.org/wiki/" + info[3][0]
            wikipedia_url = info[3][2]
            print(f"{index + 1}. {word}")
            print(f"Description: {description}")
            print(f"Wikidata URL: {wikidata_url}")
            print(f"Wikipedia URL: {wikipedia_url}")
            print('-'*len(wikipedia_url))
        print()



if __name__ == "__main__":
    main(parse_args())
