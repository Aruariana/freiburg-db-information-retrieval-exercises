from typing import Callable

from table import Table, Row


def project(
    table: Table,
    columns: list[int],
    distinct: bool = False
) -> Table:
    """

    Selects the given columns by index from the table.
    If distinct is true, makes sure to return unique rows.

    >>> t = Table.build_from_file("persons.example.tsv")
    >>> project(t, [1, 2]) \
    # doctest: +NORMALIZE_WHITESPACE
    table: persons.example
    name  | age
    -----------
    John  | 29
    Mary  | 18
    Peter | 38
    Jane  | ?
    Mark  | 38
    >>> project(t, [2]) \
    # doctest: +NORMALIZE_WHITESPACE
    table: persons.example
    age
    ---
    29
    18
    38
    ?
    38
    >>> project(t, [2], distinct=True) \
    # doctest: +NORMALIZE_WHITESPACE
    table: persons.example
    age
    ---
    29
    18
    38
    ?
    """
    assert len(columns) > 0, "zero columns given"
    assert all(0 <= col < len(table.columns) for col in columns), \
        "at least one column out of range"
    # TODO: return a new table that contains only the specified columns;
    # if distinct is True, remove duplicate rows

    slc_cols : list[str] = []
    for col_idx in columns:
        slc_cols.append(table.columns[col_idx])

    slc_rows : list[tuple[str | None, ...]] = []
    for row in table.rows:
        a_row = []
        for col_idx in columns:
            a_row.append(row[col_idx])
        # if distinct:
        #     if tuple(a_row) in slc_rows:
        #         continue

        slc_rows.append(Row(a_row))

    if distinct:
        distinct_slc_rows = []
        seen = set()
        for row in slc_rows:
            if row not in seen:
                distinct_slc_rows.append(row)
                seen.add(row)
        slc_rows = distinct_slc_rows

    return Table(table.name, slc_cols, slc_rows)

def select(
    table: Table,
    predicate: Callable[[Row], bool]
) -> Table:
    """

    Selects the rows from the table where
    the predicate evaluates to true.

    >>> t = Table.build_from_file("persons.example.tsv")
    >>> select(t, lambda row: row[1] == "John") \
    # doctest: +NORMALIZE_WHITESPACE
    table: persons.example
    id | name | age | job_id
    ------------------------
    0  | John | 29  | 0
    >>> select(t, lambda row: int(row[2] or 0) > 30) \
    # doctest: +NORMALIZE_WHITESPACE
    table: persons.example
    id | name  | age | job_id
    -------------------------
    2  | Peter | 38  | 1
    4  | Mark  | 38  | 0
    """
    # TODO: return a new table containing only the rows that satisfy
    # the predicate

    slc_rows = []
    for row in table.rows:
        if predicate(row):
            slc_rows.append(row)

    return Table(table.name, table.columns, slc_rows)


def join(
    table: Table,
    other: Table,
    column: int,
    other_column: int
) -> Table:
    """

    Joins the two tables on the given column indices using
    a hash-based equi-join.

    >>> p = Table.build_from_file("persons.example.tsv")
    >>> p.name = "persons" # overwrite name of the table for brevity
    >>> j = Table.build_from_file("jobs.example.tsv")
    >>> j.name = "jobs" # overwrite name of the table for brevity
    >>> X = join(p, j, 3, 0)
    >>> # sort by person id to make output deterministic
    >>> X.rows = sorted(X.rows, key=lambda row: row[0])
    >>> X # doctest: +NORMALIZE_WHITESPACE
    table: persons X jobs
    id | name  | age | job_id | id | job_title
    --------------------------------------------------
    0  | John  | 29  | 0      | 0  | manager
    1  | Mary  | 18  | 2      | 2  | software engineer
    2  | Peter | 38  | 1      | 1  | secretary
    3  | Jane  | ?   | 1      | 1  | secretary
    4  | Mark  | 38  | 0      | 0  | manager
    """
    assert (
        0 <= column < len(table.columns)
        and 0 <= other_column < len(other.columns)
    ),  "at least one column out of range"
    # TODO: join the two tables on the specified column indices and
    # return a new table that contains the result of the join;
    # the name of the result table should be the names of the two joined
    # tables concatenated with " X "

    equi_hash = {}
    for i in range(len(table.rows)):
        x_row = table.rows[i]
        item = x_row[column]
        if item not in equi_hash:
            equi_hash[item] = []
        equi_hash[item].append(i)

    all_rows = []
    for i in range(len(other.rows)):
        y_row = other.rows[i]
        item = y_row[other_column]

        if item in equi_hash:
            for idx in equi_hash[item]:
                x_row = table.rows[idx]
                all_rows.append(x_row + y_row)

    return Table(table.name + " X " + other.name, table.columns + other.columns, all_rows)