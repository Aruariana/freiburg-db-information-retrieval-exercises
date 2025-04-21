"""
Copyright 2019, University of Freiburg
Chair of Algorithms and Data Structures.
Claudius Korzen <korzen@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
Sebastian Walter <swalter@cs.uni-freiburg.de>
"""

import argparse

from inverted_index import InvertedIndex  # NOQA


class Evaluate:
    """
    Class for evaluating the InvertedIndex class against a benchmark.
    """

    def read_benchmark(self, file_name: str) -> dict[str, set[int]]:
        """
        Read a benchmark from the given file. The expected format of the file
        is one query per line, with the ids of all documents relevant for that
        query, like: <query>TAB<id1>WHITESPACE<id2>WHITESPACE<id3> ...

        >>> evaluate = Evaluate()
        >>> benchmark = evaluate.read_benchmark("example-benchmark.tsv")
        >>> sorted(benchmark.items())
        [('animated film', {1, 3, 4}), ('short film', {3, 4})]
        """
        # TODO: add your code

        benchmark : dict[str, set[int]] = {}

        with open(file_name, "r", encoding="utf8") as file:

            for line in file:

                results = set()
                query, raw_results = line.split("\t", 1)

                for result in raw_results.split(" "):
                    results.add(int(result))

                benchmark[query] = results

        return benchmark


    def evaluate(
        self,
        ii: InvertedIndex,
        benchmark: dict[str, set[int]],
        use_refinements: bool = False
    ) -> tuple[float, float, float]:
        """
        Evaluate the given inverted index against the given benchmark as
        follows. Process each query in the benchmark with the given inverted
        index and compare the result list with the groundtruth in the
        benchmark. For each query, compute the measure P@3, P@R and AP as
        explained in the lecture. Aggregate the values to the three mean
        measures MP@3, MP@R and MAP and return them.

        Implement a parameter 'use_refinements' that controls the use of
        ranking refinements on calling the method process_query of your
        inverted index.

        >>> ii = InvertedIndex()
        >>> ii.build_from_file("example.tsv", b=0.75, k=1.75)
        >>> evaluator = Evaluate()
        >>> benchmark = evaluator.read_benchmark("example-benchmark.tsv")
        >>> measures = evaluator.evaluate(ii, benchmark, use_refinements=False)
        >>> [round(measure, 3) for measure in measures]
        [0.667, 0.833, 0.694]
        """
        # TODO: add your code

        list_p_at_3 = []
        list_p_at_r = []
        list_ap = []

        for query in benchmark:
            result_ids = [item[0] for item in ii.process_query(ii.get_keywords(query))]
            relevant_ids = benchmark[query]

            p_at_3 = self.precision_at_k(result_ids, relevant_ids, 3)
            list_p_at_3.append(p_at_3)

            p_at_r = self.precision_at_k(result_ids, relevant_ids, len(relevant_ids))
            list_p_at_r.append(p_at_r)

            ap = self.average_precision(result_ids, relevant_ids)
            list_ap.append(ap)

        return sum(list_p_at_3)/len(list_p_at_3), sum(list_p_at_r)/len(list_p_at_r), sum(list_ap)/len(list_ap)


    def precision_at_k(
        self,
        result_ids: list[int],
        relevant_ids: set[int],
        k: int
    ) -> float:
        """
        Compute the measure P@k for the given list of result ids as it was
        returned by the inverted index for a single query, and the given set of
        relevant document ids.

        >>> evaluator = Evaluate()
        >>> evaluator.precision_at_k([5, 3, 6, 1, 2], {1, 2, 5, 6, 7, 8}, k=0)
        0.0
        >>> evaluator.precision_at_k([5, 3, 6, 1, 2], {1, 2, 5, 6, 7, 8}, k=4)
        0.75
        >>> evaluator.precision_at_k([5, 3, 6, 1, 2], {1, 2, 5, 6, 7, 8}, k=8)
        0.5
        >>> evaluator.precision_at_k([], {1, 2, 5, 6, 7, 8}, k=5)
        0.0
        >>> evaluator.precision_at_k([3, 4], {1, 2, 5, 6, 7, 8}, k=5)
        0.0
        """
        # TODO: add your code

        if k == 0:
            return 0.0

        count = 0
        iterate = len(result_ids) if k > len(result_ids) else k

        for i in range(iterate):
            if result_ids[i] in relevant_ids:
                count += 1

        return count / k


    def average_precision(
        self,
        result_ids: list[int],
        relevant_ids: set[int]
    ) -> float:
        """
        Compute the average precision (AP) for the given list of result ids as
        it was returned by the inverted index for a single query, and the given
        set of relevant document ids.

        >>> evaluator = Evaluate()
        >>> evaluator.average_precision([7, 17, 9, 42, 5], {5, 7, 12, 42})
        0.525
        >>> evaluator.average_precision([], {5, 7, 12, 42})
        0.0
        >>> evaluator.average_precision([1, 3], {5, 7, 12, 42})
        0.0
        >>> evaluator.average_precision([5, 7], {5, 7, 12, 42})
        0.5
        """
        # TODO: add your code

        ap_list = []

        for element in relevant_ids:
            if element in result_ids:
                pos = result_ids.index(element)
                ap_list.append(self.precision_at_k(result_ids, relevant_ids, pos+1))
            else:
                ap_list.append(0.0)

        return sum(ap_list)/len(ap_list)



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
        "benchmark",
        type=str,
        help="the benchmark file to use for evaluation",
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
    Constructs an inverted index from the given dataset and evaluates the
    inverted index against the given benchmark.
    """
    # TODO: add your code

    ii = InvertedIndex()
    ii.build_from_file(args.file, b=args.b_param, k=args.k_param)
    evaluator = Evaluate()
    benchmark = evaluator.read_benchmark(args.benchmark)
    measures = evaluator.evaluate(ii, benchmark, use_refinements=False)
    print([round(measure, 3) for measure in measures])


if __name__ == "__main__":
    main(parse_args())
