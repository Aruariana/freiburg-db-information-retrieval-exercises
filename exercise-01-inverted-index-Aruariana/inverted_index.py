"""
Copyright 2019, University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
Claudius Korzen <korzen@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
Natalie Prange <prange@cs.uni-freiburg.de>
Sebastian Walter <swalter@cs.uni-freiburg.de>
"""

import argparse
import re


class InvertedIndex:
    """
    A simple inverted index as explained in lecture 1.
    """

    def __init__(self) -> None:
        """
        Creates an empty inverted index.
        """
        # the inverted lists of record ids
        self.inverted_lists: dict[str, list[int]] = {}
        # the records, a list of tuples (title, description)
        self.records: list[tuple[str, str]] = []

    def get_keywords(self, query: str) -> list[str]:
        """
        Returns the keywords of the given query.
        """
        return re.findall(r"[A-Za-z]+", query.lower())

    def build_from_file(self, file_name: str) -> None:
        """
        Constructs the inverted index from given file in linear time (linear in
        the number of words in the file). The expected format of the file is
        one record per line, in the format
        <title>TAB<description>TAB<num_ratings>TAB<rating>TAB<num_sitelinks>
        You can ignore the last three columns for now, they will become
        interesting for exercise sheet 2.

        >>> ii = InvertedIndex()
        >>> ii.build_from_file("example.tsv")
        >>> sorted(ii.inverted_lists.items())
        [('a', [1, 2]), ('doc', [1, 2, 3]), ('film', [2]), ('movie', [1, 3])]
        >>> ii.records # doctest: +NORMALIZE_WHITESPACE
        [('Doc 1', 'A movie movie.'), ('Doc 2', 'A film.'),
         ('Doc 3', 'Movie.')]
        """
        # TODO: make sure that each inverted list contains a particular record
        # id at most once, even if the respective word occurs multiple times in
        # the same record. also cache the titles and descriptions of the movies
        # in self.records to use them later for output.
        with open(file_name, "r", encoding="utf-8") as file:  # I get an error, if I don't specify encoding as "utf-8"
            record_id = 0
            for line in file:
                line = line.strip()
                record_id += 1

                keywords = self.get_keywords(line)

                words_seen = set()

                for word in keywords:
                    if word not in words_seen:
                        words_seen.add(word)
                        if word not in self.inverted_lists:
                            # the word is seen for first time, create a new list
                            self.inverted_lists[word] = []
                        self.inverted_lists[word].append(record_id)

                title, desc, _ = line.split("\t", 2)
                self.records.append((title, desc))

    def intersect(self, list1: list[int], list2: list[int]) -> list[int]:
        """
        Computes the intersection of the two given inverted lists in linear
        time (linear in the total number of elements in the two lists).

        >>> ii = InvertedIndex()
        >>> ii.intersect([1, 5, 7], [2, 4])
        []
        >>> ii.intersect([1, 2, 5, 7], [1, 3, 5, 6, 7, 9])
        [1, 5, 7]
        """
        # TODO: add your code here
        idx_1 = idx_2 = 0
        intersect = []

        while idx_1 < len(list1) and idx_2 < len(list2):
            if list1[idx_1] > list2[idx_2]:
                idx_2 += 1
            elif list1[idx_1] < list2[idx_2]:
                idx_1 += 1
            else:
                intersect.append(list1[idx_1])
                idx_1 += 1
                idx_2 += 1

        return intersect

    def process_query(self, keywords: list[str]) -> list[int]:
        """
        Processes the given keyword query as follows: Fetches the inverted list
        for each of the keywords in the given query and computes the
        intersection of all inverted lists (which is empty, if there is a
        keyword in the query which has no inverted list in the index).

        >>> ii = InvertedIndex()
        >>> ii.build_from_file("example.tsv")
        >>> ii.process_query([])
        []
        >>> ii.process_query(["doc"])
        [1, 2, 3]
        >>> ii.process_query(["doc", "movie"])
        [1, 3]
        >>> ii.process_query(["doc", "movie", "comedy"])
        []
        """
        # TODO: add your code here

        if not keywords:
            return []

        for keyword in keywords:
            if keyword not in self.inverted_lists:
                return []

        intersection = self.inverted_lists[keywords[0]]
        for keyword in keywords[1:]:
            intersection = self.intersect(intersection, self.inverted_lists[keyword])

        return intersection


def parse_args() -> argparse.Namespace:
    """
    Defines and parses command line arguments for this script.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        type=str,
        help="the file from which to construct the inverted index",
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    """
    Constructs an inverted index from a given text file, then asks the user in
    an infinite loop for keyword queries and outputs the title and description
    of up to three matching records.
    """
    # create a new inverted index from the given file
    print(f"Reading from file {args.file}")
    ii = InvertedIndex()
    ii.build_from_file(args.file)

    # TODO: add your code here
    # Break out of the code if no query is given
    while True:
        keywords = ii.get_keywords(input("Query: "))
        if not keywords:
            break
        outputs = ii.process_query(keywords)
        length = 3 if len(outputs) > 3 else len(outputs)
        for i in range(length):
            title, description = ii.records[outputs[i]-1]
            for keyword in keywords:

                # Got this part from ChatGPT to highlight the word
                # The issue was the case differences, I wanted to keep the case intact
                # while still highlighting the word
                def bold_replacer(match):
                    return f"\033[31m{match.group(0)}\033[0m"

                title = re.sub(fr"(?i)\b{keyword}\b", bold_replacer, title)
                description = re.sub(fr"(?i)\b{keyword}\b", bold_replacer, description)
            print(f"\n{i+1}.\nTitle : {title}\nDescription : {description}\n")


if __name__ == "__main__":
    main(parse_args())
