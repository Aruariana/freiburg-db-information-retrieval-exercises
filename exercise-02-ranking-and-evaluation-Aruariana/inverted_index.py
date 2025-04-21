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
import re
import argparse


class InvertedIndex:
    """
    A simple inverted index that uses BM25 scores.
    """

    def __init__(self) -> None:
        """
        Creates an empty inverted index.
        """
        # the inverted lists of tuples (doc id, score)
        self.inverted_lists: dict[str, list[tuple[int, float]]] = {}
        # the docs, a list of tuples (title, description)
        self.docs: list[tuple[str, str]] = []

    def get_keywords(self, query: str) -> list[str]:
        """
        Returns the keywords of the given query.
        """
        return re.findall(r"[A-Za-z]+", query.lower())

    def build_from_file(
        self,
        file_name: str,
        b: float,
        k: float
    ) -> None:
        """
        Construct the inverted index from the given file. The expected format
        of the file is one document per line, in the format
        <title>TAB<description>TAB<num_ratings>TAB<rating>TAB<num_sitelinks>
        Each entry in the inverted list associated to a word should contain a
        document id and a BM25 score. Compute the BM25 scores as follows:

        (1) In a first pass, compute the inverted lists with tf scores (that
            is the number of occurrences of the word within the <title> and the
            <description> of a document). Further, compute the document length
            (DL) for each document (that is the number of words in the <title>
            and the <description> of a document). Afterwards, compute the
            average document length (AVDL).
        (2) In a second pass, iterate over all inverted lists and replace the
            tf scores by BM25 scores, defined as:
            BM25 = tf * (k+1) / (k * (1 - b + b * DL/AVDL) + tf) * log2(N/df),
            where N is the total number of documents and df is the number of
            documents that contain the word.

        >>> ii = InvertedIndex()
        >>> ii.build_from_file("example.tsv", b=0.0, k=float("inf"))
        >>> inv_lists = sorted(ii.inverted_lists.items())
        >>> [(w, [(i, '%.3f' % tf) for i, tf in l]) for w, l in inv_lists]
        ... # doctest: +NORMALIZE_WHITESPACE
        [('animated', [(1, '0.415'), (2, '0.415'), (4, '0.415')]),
         ('animation', [(3, '2.000')]),
         ('film', [(2, '1.000'), (4, '1.000')]),
         ('movie', [(1, '0.000'), (2, '0.000'), (3, '0.000'), (4, '0.000')]),
         ('non', [(2, '2.000')]),
         ('short', [(3, '1.000'), (4, '2.000')])]

        >>> ii = InvertedIndex()
        >>> ii.build_from_file("example.tsv", b=0.75, k=1.75)
        >>> inv_lists = sorted(ii.inverted_lists.items())
        >>> [(w, [(i, '%.3f' % tf) for i, tf in l]) for w, l in inv_lists]
        ... # doctest: +NORMALIZE_WHITESPACE
        [('animated', [(1, '0.459'), (2, '0.402'), (4, '0.358')]),
         ('animation', [(3, '2.211')]),
         ('film', [(2, '0.969'), (4, '0.863')]),
         ('movie', [(1, '0.000'), (2, '0.000'), (3, '0.000'), (4, '0.000')]),
         ('non', [(2, '1.938')]),
         ('short', [(3, '1.106'), (4, '1.313')])]

        >>> ii = InvertedIndex()
        >>> ii.build_from_file("example.tsv", b=0.0, k=0.0)
        >>> inv_lists = sorted(ii.inverted_lists.items())
        >>> [(w, [(i, '%.3f' % tf) for i, tf in l]) for w, l in inv_lists]
        ... # doctest: +NORMALIZE_WHITESPACE
        [('animated', [(1, '0.415'), (2, '0.415'), (4, '0.415')]),
         ('animation', [(3, '2.000')]),
         ('film', [(2, '1.000'), (4, '1.000')]),
         ('movie', [(1, '0.000'), (2, '0.000'), (3, '0.000'), (4, '0.000')]),
         ('non', [(2, '2.000')]),
         ('short', [(3, '1.000'), (4, '1.000')])]
        """
        # TODO: change this code to compute tf scores and document lengths
        with open(file_name, "r", encoding="utf8") as file:

            dl: list[int] = []

            doc_id = 0
            for line in file:
                doc_id += 1

                # store the doc as a tuple (title, description).
                title, desc, _ = line.split("\t", 2)
                self.docs.append((title, desc))

                keywords = self.get_keywords(title) + self.get_keywords(desc)

                dl.append(len(keywords))

                for word in keywords:
                    if word not in self.inverted_lists:
                        # the word is seen for first time, create a new list.
                        self.inverted_lists[word] = [(doc_id, 1)]
                    elif self.inverted_lists[word][-1][0] == doc_id:
                        # make sure that the list contains the id at most once.
                        self.inverted_lists[word][-1] = (self.inverted_lists[word][-1][0], self.inverted_lists[word][-1][1]+1)
                    else:
                        self.inverted_lists[word].append((doc_id, 1))

                    # print(word, self.inverted_lists[word])


            avdl : float = sum(dl)/len(dl)

        # TODO: add your code to compute the final inverted index
        # with BM25 scores

        for word in self.inverted_lists:

            df = len(self.inverted_lists[word])

            for i in range(len(self.inverted_lists[word])):
                doc_id, doc_tf = self.inverted_lists[word][i]
                doc_dl = dl[doc_id-1]

                if math.isinf(k):
                    bm25_score = doc_tf * math.log2(len(self.docs)/df)
                else:
                    bm25_score = (doc_tf * (k+1)) / (k * (1 - b + b * doc_dl/avdl) + doc_tf) * math.log2(len(self.docs)/df)

                self.inverted_lists[word][i] = (doc_id, bm25_score)





    def merge(
        self,
        list1: list[tuple[int, float]],
        list2: list[tuple[int, float]],
    ) -> list[tuple[int, float]]:
        """
        Compute the union of the two given inverted lists in linear time
        (linear in the total number of entries in the two lists), where the
        entries in the inverted lists are postings of form (doc_id, bm25_score)
        and are expected to be sorted by doc_id, in ascending order.

        >>> ii = InvertedIndex()
        >>> l1 = ii.merge([(1, 2.1), (5, 3.2)], [(1, 1.7), (2, 1.3), (6, 3.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l1]
        [(1, '3.8'), (2, '1.3'), (5, '3.2'), (6, '3.3')]

        >>> l2 = ii.merge([(3, 1.7), (5, 3.2), (7, 4.1)], [(1, 2.3), (5, 1.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3'), (3, '1.7'), (5, '4.5'), (7, '4.1')]

        >>> l2 = ii.merge([], [(1, 2.3), (5, 1.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3'), (5, '1.3')]

        >>> l2 = ii.merge([(1, 2.3)], [])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3')]

        >>> l2 = ii.merge([], [])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        []
        """
        # TODO: add your code
        idx_1 = idx_2 = 0
        intersect: list[tuple[int, float]] = []

        while idx_1 < len(list1) and idx_2 < len(list2):
            if list1[idx_1][0] > list2[idx_2][0]:
                intersect.append(list2[idx_2])
                idx_2 += 1
            elif list1[idx_1][0] < list2[idx_2][0]:
                intersect.append(list1[idx_1])
                idx_1 += 1
            else:
                intersect.append((list1[idx_1][0], list1[idx_1][1] + list2[idx_2][1]))
                idx_1 += 1
                idx_2 += 1

        while idx_1 < len(list1):
            intersect.append(list1[idx_1])
            idx_1 += 1

        while idx_2 < len(list2):
            intersect.append(list2[idx_2])
            idx_2 += 1

        return intersect


    def process_query(
        self,
        keywords: list[str],
        use_refinements: bool = False
    ) -> list[tuple[int, float]]:
        """
        Process the given keyword query as follows: Fetch the inverted list for
        each of the keywords in the query and compute the union of all lists.
        Sort the resulting list by BM25 scores in descending order.

        This method returns all results for the given query, not just the
        top 3!

        If you want to implement some ranking refinements, make these
        refinements optional (their use should be controllable via the
        use_refinements flag).

        >>> ii = InvertedIndex()
        >>> ii.inverted_lists = {
        ... "foo": [(1, 0.2), (3, 0.6)],
        ... "bar": [(1, 0.4), (2, 0.7), (3, 0.5)],
        ... "baz": [(2, 0.1)]}
        >>> result = ii.process_query(["foo", "bar"])
        >>> [(id, "%.1f" % tf) for id, tf in result]
        [(3, '1.1'), (2, '0.7'), (1, '0.6')]
        >>> result = ii.process_query(["bar"])
        >>> [(id, "%.1f" % tf) for id, tf in result]
        [(2, '0.7'), (3, '0.5'), (1, '0.4')]
        >>> result = ii.process_query(["barb"])
        >>> [(id, "%.1f" % tf) for id, tf in result]
        []
        >>> result = ii.process_query(["foo", "bar", "baz"])
        >>> [(id, "%.1f" % tf) for id, tf in result]
        [(3, '1.1'), (2, '0.8'), (1, '0.6')]
        >>> result = ii.process_query([""])
        >>> [(id, "%.1f" % tf) for id, tf in result]
        []
        """
        # TODO: add your code

        if not keywords:
            return []

        results = []

        for i in range(0, len(keywords)):
            if keywords[i] in self.inverted_lists:
                results = self.merge(results, self.inverted_lists[keywords[i]])

        results = sorted(results, key= lambda x: x[1], reverse=True)

        return results


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
    parser.add_argument(
        "-b",
        "--b-param",
        type=float,
        default=0.75,
        help="the b parameter for BM25",
    )
    parser.add_argument(
        "-k",
        "--k-param",
        type=float,
        default=1.75,
        help="the k parameter for BM25",
    )
    parser.add_argument(
        "--use-refinements",
        action="store_true",
        help="whether to use refinements"
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
    ii.build_from_file(args.file, args.b_param, args.k_param)

    # TODO: add your code here
    while True:
        keywords = ii.get_keywords(input("Query: "))
        if not keywords:
            break
        outputs = ii.process_query(keywords)
        length = 3 if len(outputs) > 3 else len(outputs)
        for i in range(length):
            title, description = ii.docs[outputs[i][0]-1]
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
 
