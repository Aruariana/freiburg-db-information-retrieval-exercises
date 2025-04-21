import argparse
import re
import time
from typing import Callable

from table import Table
from operations import (
    join,
    select,
    project
)


def timeit(
    f: Callable[[dict[str, Table]], Table],
    tables: dict[str, Table],
    n: int
) -> tuple[Table, int]:
    """

    Runs function f on tables n times and returns the
    result table and average runtime in milliseconds.

    """
    assert n > 0, "n must be greater than 0"
    # init empty table
    table = Table("dummy", [], [])
    start = time.perf_counter()
    for _ in range(n):
        table = f(tables)
    end = time.perf_counter()
    return table, round(1000 * (end - start) / n)


def run_example_sequence(tables: dict[str, Table]) -> Table:
    """

    Runs a sequence of relational operations on the tables
    for the given example query and SQL.

    Query:
    Names and birth dates of all actors in the movie Avatar.

    SQL:
    SELECT p.name, p.birth_date
    FROM movies m, roles r, persons p
    WHERE m.title = "Avatar"
    AND r.movie_id = m.movie_id
    AND r.person_id = p.person_id;

    """
    # get movies with title Avatar
    avatar = select(
        tables["movies"],
        lambda row: row[1] == "Avatar"
    )
    # join avatar movies with roles table on movie_id
    avatar_actors = join(
        avatar,
        tables["roles"],
        0,
        0
    )
    # join avatar actors with persons so we get the name and birth date
    # information
    avatar_actor_infos = join(
        avatar_actors,
        tables["persons"],
        avatar.shape[1] + 1,
        0
    )
    # only select name and birth date columns from final table
    _, num_cols = avatar_actor_infos.shape
    avatar_actor_names = project(
        avatar_actor_infos,
        [num_cols - 2, num_cols - 1]
    )
    return avatar_actor_names


def run_sequence_1(tables: dict[str, Table]) -> Table:
    """

    Runs the first sequence of relational operations on the tables
    for the given query and SQL.

    Query:
    Actors who won a Golden Globe for a movie with an IMDb
    score of 8.0 or higher since 2010, including the name of
    the movie, the role played, and the type of Golden Globe award.

    SQL:
    SELECT m.title, p.name, r.role, an.award_name
    FROM movies m, awards a, persons p, roles r, award_names an
    WHERE an.award_name LIKE "Golden Globe Award for Best Act%"
    AND a.movie_id = m.movie_id
    AND a.person_id = p.person_id
    AND a.award_id = an.award_id
    AND r.movie_id = m.movie_id
    AND r.person_id = p.person_id
    AND CAST(m.year AS INT) >= 2010
    AND CAST(m.imdb_score AS REAL) >= 8.0;

    """
    # TODO: code your first sequence of operations here;
    # see run_example_sequence for an example how that
    # should look like. make sure to add explanatory
    # comments before each operation

    # Select the movies with score higher than 8 and newer than 2010
    movies_8_2010 = select(
        tables["movies"],
        lambda row: float(row[4] or 0) >= 8.0 and float(row[2] or 0) >= 2010
    )

    # Select the wanted awards
    pattern = r'^Golden Globe Award for Best Act.*'
    global_award_names = select(
        tables["award_names"],
        lambda row: bool(re.match(pattern, row[1]))
    )

    # Join awards
    awards = join(
        tables["awards"],
        global_award_names,
        2,
        0
    )

    # Join movies and roles
    movies_roles = join(
        movies_8_2010,
        tables["roles"],
        0,
        0
    )

    # Join persons to movies_roles
    movies_roles_persons = join(
        movies_roles,
        tables["persons"],
        6,
        0
    )

    # Join awards to movies_roles_persons
    movies_roles_persons_awards1 = join(
        movies_roles_persons,
        awards,
        0,
        0
    )

    movies_roles_persons_awards2 = select(
        movies_roles_persons_awards1,
        lambda row: row[6] == row[-4]
    )

    # Projection

    selected_movies_roles_persons_awards = project(
        movies_roles_persons_awards2,
        [1, 9, 7, 15],
        False
    )

    return selected_movies_roles_persons_awards


def run_sequence_2(tables: dict[str, Table]) -> Table:
    """

    Runs the second sequence of relational operations on the tables
    for the given query and SQL.

    Query:
    Actors who won a Golden Globe for a movie with an IMDb
    score of 8.0 or higher since 2010, including the name of
    the movie, the role played, and the type of Golden Globe award.

    SQL:
    SELECT m.title, p.name, r.role, an.award_name
    FROM movies m, awards a, persons p, roles r, award_names an
    WHERE an.award_name LIKE "Golden Globe Award for Best Act%"
    AND a.movie_id = m.movie_id
    AND a.person_id = p.person_id
    AND a.award_id = an.award_id
    AND r.movie_id = m.movie_id
    AND r.person_id = p.person_id
    AND CAST(m.year AS INT) >= 2010
    AND CAST(m.imdb_score AS REAL) >= 8.0;

    """
    # TODO: code your second sequence of operations here;
    # see run_example_sequence for an example how that
    # should look like. make sure to add explanatory
    # comments before each operation

    # Select the movies with score higher than 8 and newer than 2010
    movies_8_2010 = select(
        tables["movies"],
        lambda row: float(row[4] or 0) >= 8.0 and float(row[2] or 0) >= 2010
    )

    # Select the wanted awards
    pattern = r'^Golden Globe Award for Best Act.*'
    global_award_names = select(
        tables["award_names"],
        lambda row: bool(re.match(pattern, row[1]))
    )

    # Join awards
    awards = join(
        tables["awards"],
        global_award_names,
        2,
        0
    )

    # Join movies and roles
    movies_roles = join(
        movies_8_2010,
        tables["roles"],
        0,
        0
    )

    # Join persons to movies_roles
    movies_roles_persons = join(
        movies_roles,
        tables["persons"],
        6,
        0
    )

    # Join awards to movies_roles_persons
    movies_roles_persons_awards1 = join(
        movies_roles_persons,
        awards,
        0,
        0
    )

    movies_roles_persons_awards2 = select(
        movies_roles_persons_awards1,
        lambda row: row[6] == row[-4]
    )

    # Projection

    selected_movies_roles_persons_awards = project(
        movies_roles_persons_awards2,
        [1, 9, 7, 15],
        False
    )

    return selected_movies_roles_persons_awards


def run_sequence_3(tables: dict[str, Table]) -> Table:
    """

    Runs the third sequence of relational operations on the tables
    for the given query and SQL.

    Query:
    Actors who won a Golden Globe for a movie with an IMDb
    score of 8.0 or higher since 2010, including the name of
    the movie, the role played, and the type of Golden Globe award.

    SQL:
    SELECT m.title, p.name, r.role, an.award_name
    FROM movies m, awards a, persons p, roles r, award_names an
    WHERE an.award_name LIKE "Golden Globe Award for Best Act%"
    AND a.movie_id = m.movie_id
    AND a.person_id = p.person_id
    AND a.award_id = an.award_id
    AND r.movie_id = m.movie_id
    AND r.person_id = p.person_id
    AND CAST(m.year AS INT) >= 2010
    AND CAST(m.imdb_score AS REAL) >= 8.0;

    """
    # TODO: code your third sequence of operations here;
    # see run_example_sequence for an example how that
    # should look like. make sure to add explanatory
    # comments before each operation

    # Select the movies with score higher than 8 and newer than 2010
    movies_8_2010 = select(
        tables["movies"],
        lambda row: float(row[4] or 0) >= 8.0 and float(row[2] or 0) >= 2010
    )

    # Select the wanted awards
    pattern = r'^Golden Globe Award for Best Act.*'
    global_award_names = select(
        tables["award_names"],
        lambda row: bool(re.match(pattern, row[1]))
    )

    # Join awards
    awards = join(
        tables["awards"],
        global_award_names,
        2,
        0
    )

    # Join movies and roles
    movies_roles = join(
        movies_8_2010,
        tables["roles"],
        0,
        0
    )

    # Join persons to movies_roles
    movies_roles_persons = join(
        movies_roles,
        tables["persons"],
        6,
        0
    )

    # Join awards to movies_roles_persons
    movies_roles_persons_awards1 = join(
        movies_roles_persons,
        awards,
        0,
        0
    )

    movies_roles_persons_awards2 = select(
        movies_roles_persons_awards1,
        lambda row: row[6] == row[-4]
    )

    # Projection

    selected_movies_roles_persons_awards = project(
        movies_roles_persons_awards2,
        [1, 9, 7, 15],
        False
    )

    return selected_movies_roles_persons_awards



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
        "--example",
        action="store_true",
        help="execute the example query only"
    )
    parser.add_argument(
        "-n",
        "--n-times",
        type=int,
        default=3,
        help="number of times each sequence will be executed "
        "to measure runtime"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="whether to print the full untruncated table"
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    print("Loading tables from files...")
    tables = {}
    for file in args.tables:
        table = Table.build_from_file(file)
        assert table.name not in tables, \
            f"table with name {table.name} already exists"
        tables[table.name] = table

    if args.example:
        # run example sequence and measure runtime
        result, runtime = timeit(run_example_sequence, tables, args.n_times)
        print(result)
        print(f"Example sequence took {runtime:,}ms")
        return

    # run all three sequences and measure runtimes
    glob = globals()
    runtimes = []
    results = []
    for i in range(3):
        result, runtime = timeit(
            glob[f"run_sequence_{i + 1}"],
            tables,
            args.n_times
        )
        runtimes.append(runtime)
        results.append(result)

    # make sure all three sequences return the same result
    assert all(
        sorted(tuple(c or "" for c in r) for r in result.rows)
        == sorted(tuple(c or "" for c in r) for r in results[0].rows)
        for result in results[1:]
    ), "results of all three sequences must be equal"

    # print result table and runtimes
    results[0].verbose = args.verbose
    print(results[0])
    for i, runtime in enumerate(runtimes):
        print(f"Sequence {i+1} took {runtime:,}ms")


if __name__ == "__main__":
    main(parse_args())
 