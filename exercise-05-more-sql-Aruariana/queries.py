import argparse
import re
from timeit import repeat
from typing import Callable

from table import Table
from operations import (
    join,
    select,
    project,
    group_by,
    order_by,
    limit
)


def timeit(
    f: Callable[[dict[str, Table]], Table],
    tables: dict[str, Table],
    n: int
) -> tuple[Table, float]:
    """

    Runs function f on tables n times and returns the
    result table and average runtime in milliseconds.

    """
    assert n > 0, "n must be greater than 0"
    # we replaced our own timeit implementation with the
    # timeit module from the standard library, which returns
    # more accurate and reliable results
    runtimes = repeat(
        "f(tables)",
        globals=locals(),
        number=n,
        repeat=5
    )
    runtime = sum(runtimes) / len(runtimes)
    # get final table
    table = f(tables)
    return table, 1000.0 * runtime / n


def run_sequence_1(tables: dict[str, Table]) -> Table:
    """

    Runs the first sequence of relational operations on the tables
    for the given query and SQL.

    Query:
    All movies that won an Oscar (in any category)
    and were released in 2000, 2001, 2002, or 2003.

    SQL:
    SELECT DISTINCT m.title
    FROM movies m, awards a, award_names an
    WHERE m.movie_id = a.movie_id
    AND a.award_id = an.award_id
    AND an.award_name LIKE "Academy Award%"
    AND CAST(m.year AS INT) BETWEEN 2000 AND 2003;

    """
    # TODO: enter the first sequence of operations here

    movies = tables['movies']
    awards = tables['awards']
    award_names = tables['award_names']

    # Join movies and awards
    m_a = join(movies, awards, 0, 0)

    # Join movies/awards and award_names
    m_a_an = join(m_a, award_names, m_a.shape[1] - 1, 0)

    # Select Academy Awards
    m_a_an_academy = select(m_a_an, lambda row: bool(re.match(r"^Academy Award.*", row[-1])))

    # Select movies between 2000 and 2003
    m_a_an_academy_year = select(m_a_an_academy, lambda row: 2000 <= int(row[2] or 0) <= 2003)

    # Project title
    m_a_an_academy_year_title = project(m_a_an_academy_year, [1], True)

    return m_a_an_academy_year_title


def calc_cost_1(tables: dict[str, Table]) -> float:
    """

    Calculates the cost of the first sequence of relational operations.
    If you did the cost calculation by hand, just
    return your final cost estimate here.

    """
    # TODO: estimate the cost of the first sequence of operations
    # and return the cost estimate here

    m_rows, m_cols = tables["movies"].shape
    a_rows, a_cols = tables["awards"].shape
    an_rows, an_cols = tables["award_names"].shape

    cost = 0

    # Join of movies and awards
    t1_rows = min(m_rows, a_rows)
    t1_cols = m_cols + a_cols
    cost += m_rows + a_rows + t1_rows*t1_cols

    # Join award_names to the prev table
    t2_rows = min(t1_rows, an_rows)
    t2_cols = t1_cols + an_cols
    cost += t1_rows + an_rows + t2_rows*t2_cols

    # Select "Academy Award%"
    cost += t2_rows * t2_cols
    t2_rows = t2_rows // 2

    # Select "year" between 2000 and 2003

    cost += t2_rows * t2_cols
    t2_rows = t2_rows // 2

    # Project title

    t2_cols = 1
    cost += t2_rows * t2_cols

    return cost


def run_sequence_2(tables: dict[str, Table]) -> Table:
    """

    Runs the second sequence of relational operations on the tables
    for the given query and SQL.

    Query:
    All movies that won an Oscar (in any category)
    and were released in 2000, 2001, 2002, or 2003.

    SQL:
    SELECT DISTINCT m.title
    FROM movies m, awards a, award_names an
    WHERE m.movie_id = a.movie_id
    AND a.award_id = an.award_id
    AND an.award_name LIKE "Academy Award%"
    AND CAST(m.year AS INT) BETWEEN 2000 AND 2003;

    """
    # TODO: enter the second sequence of operations here

    movies = tables['movies']
    awards = tables['awards']
    award_names = tables['award_names']

    # Select award_names
    award_names = select(award_names, lambda row: bool(re.match(r"^Academy Award.*", row[1])))

    # Select movies between 2000 and 2003
    movies = select(movies, lambda row: 2000 <= (int(row[2] or 0)) <= 2003)

    # Join movies and awards
    m_a = join(movies, awards, 0, 0)

    # Join award_names to prev table
    m_a_an = join(m_a, award_names, m_a.shape[1] - 1, 0)

    # Project title
    m_a_an = project(m_a_an, [1], True)

    return m_a_an


def calc_cost_2(tables: dict[str, Table]) -> float:
    """

    Calculates the cost of the second sequence of relational operations.
    If you did the cost calculation by hand, just
    return your final cost estimate here.

    """
    # TODO: estimate the cost of the second sequence of operations
    # and return the cost estimate here

    m_rows, m_cols = tables["movies"].shape
    a_rows, a_cols = tables["awards"].shape
    an_rows, an_cols = tables["award_names"].shape

    cost = 0

    # Select award_names "Academy Award%"
    cost += an_rows * an_cols
    an_rows = an_rows // 2

    # Select movies between 2000 and 2003
    cost += m_rows * m_cols
    m_rows = m_rows // 2

    # Join movies and awards
    t1_rows = min(m_rows, a_rows)
    t1_cols = m_cols + a_cols
    cost += m_rows + a_rows + t1_rows*t1_cols

    # Join prev table and award_names
    t2_rows = min(t1_rows, an_rows)
    t2_cols = t1_cols + an_cols
    cost += t1_rows + an_rows + t2_rows*t2_cols

    # Project title
    t2_cols = 1
    cost += t2_rows * t2_cols

    return cost


def run_group_by_sequence(tables: dict[str, Table]) -> Table:
    """

    Runs a sequence of relational operations on the tables
    for the given query and SQL.

    Query:
    Top 10 directors by average IMDb score with at least 10 movies,
    considering only movies with at least 100,000 votes.

    SQL:
    SELECT
    p.name,
    COUNT(m.movie_id) AS num_movies,
    ROUND(AVG(m.imdb_score), 2) AS avg_score
    FROM movies m, persons p, directors d
    WHERE m.movie_id = d.movie_id
    AND p.person_id = d.person_id
    AND CAST(m.votes AS INT) >= 100000
    GROUP BY d.person_id
    HAVING num_movies >= 10
    ORDER BY avg_score DESC
    LIMIT 10;

    """
    # select movies with at least 100_000 votes
    movies = select(
        tables["movies"],
        lambda row: int(row[-1] or 0) >= 100000
    )

    # join movies and directors
    movies_directors = join(
        movies,
        tables["directors"],
        0,
        0
    )
    # join movies_directors and persons
    movies_directors_persons = join(
        movies_directors,
        tables["persons"],
        movies_directors.shape[1] - 1,
        0
    )
    # group by person_id
    grouped = group_by(
        movies_directors_persons,
        # group by person id and name
        [
            movies_directors.shape[1],
            movies_directors.shape[1] + 1
        ],
        [
            # num movies
            (
                0,
                lambda values: str(len(values))
            ),
            # average imdb score
            (
                4,
                lambda values: str(round(
                    sum(float(v or 0.0) for v in values)
                    / max(1, len(values)), 2
                ))
            )
        ]
    )
    # select only directors with at least 10 movies
    grouped = select(
        grouped,
        lambda row: int(row[2] or 0) >= 10
    )
    # order by avg_score
    ordered = order_by(
        grouped,
        3,
        ascending=False
    )
    # limit to 10 rows
    limited = limit(
        ordered,
        10
    )
    # get name, num movies and avg_score
    limited = project(
        limited,
        [1, 2, 3]
    )
    # rename columns (just for output purposes)
    limited.columns = ["name", "num_movies", "avg_score"]
    # print(limited)
    return limited


def run_improved_group_by_sequence(tables: dict[str, Table]) -> Table:
    """

    Runs an improved sequence of relational operations on the tables
    for the given query and SQL.

    Query:
    Top 10 directors by average IMDb score with at least 10 movies,
    considering only movies with at least 100,000 votes.

    SQL:
    SELECT
    p.name,
    COUNT(m.movie_id) AS num_movies,
    ROUND(AVG(m.imdb_score), 2) AS avg_score
    FROM movies m, persons p, directors d
    WHERE m.movie_id = d.movie_id
    AND p.person_id = d.person_id
    AND CAST(m.votes AS INT) >= 100000
    GROUP BY d.person_id
    HAVING num_movies >= 10
    ORDER BY avg_score DESC
    LIMIT 10;

    """
    # TODO: enter the improved sequence of operations here;
    # its output should be the same as the output of the
    # run_group_by_sequence function

    # select movies with at least 100_000 votes
    movies = select(
        tables["movies"],
        lambda row: int(row[-1] or 0) >= 100000
    )

    # join movies and directors
    movies_directors = join(
        movies,
        tables["directors"],
        0,
        0
    )

    # group by person_id
    grouped = group_by(
        movies_directors,
        # group by person id
        [
            movies_directors.shape[1]-1,
        ],
        [
            # num movies
            (
                0,
                lambda values: str(len(values))
            ),
            # average imdb score
            (
                4,
                lambda values: str(round(
                    sum(float(v or 0.0) for v in values)
                    / max(1, len(values)), 2
                ))
            )
        ]
    )

    # select only directors with at least 10 movies
    grouped = select(
        grouped,
        lambda row: int(row[1] or 0) >= 10
    )
    # order by avg_score
    ordered = order_by(
        grouped,
        2,
        ascending=False
    )
    # limit to 10 rows
    limited = limit(
        ordered,
        10
    )

    # join persons
    limited = join(
        limited,
        tables["persons"],
        0,
        0
    )

    # get name, num movies and avg_score
    limited = project(
        limited,
        [4, 1, 2]
    )

    # order again
    limited = order_by(
        limited,
        2,
        ascending=False
    )

    # rename columns (just for output purposes)
    limited.columns = ["name", "num_movies", "avg_score"]
    # print(limited)
    return limited


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "tables",
        nargs="+",
        type=str,
        help="paths to the tsv-files that will be read as tables"
    )
    parser.add_argument(
        "-e",
        "--exercise",
        choices=[1, 2],
        type=int,
        required=True,
        help="execute the code for the given exercise"
    )
    parser.add_argument(
        "-n",
        "--n-times",
        type=int,
        default=10,
        help="number of times each sequence will be executed "
        "to measure runtime"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="whether to print the full untruncated table"
    )
    return parser.parse_args()


def check_rows(first: Table, second: Table) -> None:
    assert (
        sorted(tuple(c or "" for c in r) for r in first.rows)
        == sorted(tuple(c or "" for c in r) for r in second.rows)
    ), "rows of the tables must be equal"


def main(args: argparse.Namespace) -> None:
    print("Loading tables from files...")
    tables = {}
    for file in args.tables:
        table = Table.build_from_file(file)
        assert table.name not in tables, \
            f"table with name {table.name} already exists"
        tables[table.name] = table

    if args.exercise == 1:
        cost_1 = calc_cost_1(tables)
        cost_2 = calc_cost_2(tables)

        result_1, runtime_1 = timeit(
            run_sequence_1,
            tables,
            args.n_times
        )
        result_2, runtime_2 = timeit(
            run_sequence_2,
            tables,
            args.n_times
        )

        check_rows(result_1, result_2)
        result_1.verbose = args.verbose
        print(result_1)

        print(f"\nCost of sequence 1: {cost_1:,.1f}")
        print(f"Cost of sequence 2: {cost_2:,.1f}")
        print(f"Cost ratio: {cost_1 / cost_2:.2f}")

        print(f"\nSequence 1 took {runtime_1:,.1f}ms")
        print(f"Sequence 2 took {runtime_2:,.1f}ms")
        print(f"Runtime ratio: {runtime_1 / runtime_2:.2f}")

        return

    result, runtime = timeit(
        run_group_by_sequence,
        tables,
        args.n_times
    )
    result_imp, runtime_imp = timeit(
        run_improved_group_by_sequence,
        tables,
        args.n_times
    )

    check_rows(result, result_imp)
    result.verbose = args.verbose
    print(result)

    print(f"\nSequence took {runtime:,.1f}ms")
    print(f"Improved sequence took {runtime_imp:,.1f}ms")
    print(f"Runtime ratio: {runtime / runtime_imp:.2f}")


if __name__ == "__main__":
    main(parse_args())
