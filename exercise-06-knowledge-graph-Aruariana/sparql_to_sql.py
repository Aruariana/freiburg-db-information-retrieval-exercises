"""
Copyright 2023, University of Freiburg,
Chair of Algorithms and Data Structures.
Authors:
Patrick Brosi <brosi@cs.uni-freiburg.de>,
Claudius Korzen <korzen@cs.uni-freiburg.de>,
Natalie Prange <prange@cs.uni-freiburg.de>,
Sebastian Walter <swalter@cs.uni-freiburg.de>
"""

import argparse
import re
import sqlite3
import time


Triple = tuple[str, str, str]


class SPARQL:
    """ A simple SPARQL engine for a SQL backend. """

    def parse_sparql(
        self,
        sparql: str
    ) -> tuple[list[str], list[Triple], tuple[str, bool] | None, int | None]:
        """

        Parses a SPARQL query into its components, a tuple of
        (variables, triples, order by, limit).

        ORDER BY and LIMIT clauses are optional, but LIMIT
        should always come after ORDER BY if both are specified.

        >>> engine = SPARQL()
        >>> engine.parse_sparql(
        ...     "SELECT ?x ?y WHERE {"
        ...     "?x pred_1 some_obj . "
        ...     "?y pred_2 ?z "
        ...     "}"
        ... ) # doctest: +NORMALIZE_WHITESPACE
        (['?x', '?y'], [('?x', 'pred_1', 'some_obj'),
        ('?y', 'pred_2', '?z')], None, None)
        >>> engine.parse_sparql(
        ...     "SELECT ?x ?y WHERE {"
        ...     "?x pred_1 some_obj . "
        ...     "?y pred_2 ?z "
        ...     "} ORDER BY DESC(?x)"
        ... ) # doctest: +NORMALIZE_WHITESPACE
        (['?x', '?y'], [('?x', 'pred_1', 'some_obj'),
        ('?y', 'pred_2', '?z')], ('?x', False), None)
        >>> engine.parse_sparql(
        ...     "SELECT ?x ?y WHERE {"
        ...     "?x pred_1 some_obj . "
        ...     "?y pred_2 ?z "
        ...     "} ORDER BY ASC(?x)"
        ... ) # doctest: +NORMALIZE_WHITESPACE
        (['?x', '?y'], [('?x', 'pred_1', 'some_obj'),
        ('?y', 'pred_2', '?z')], ('?x', True), None)
        >>> engine.parse_sparql(
        ...     "SELECT ?x ?y WHERE {"
        ...     "?x pred_1 some_obj . "
        ...     "?y pred_2 ?z "
        ...     "} ORDER BY ASC(?x) LIMIT 25"
        ... ) # doctest: +NORMALIZE_WHITESPACE
        (['?x', '?y'], [('?x', 'pred_1', 'some_obj'),
        ('?y', 'pred_2', '?z')], ('?x', True), 25)
        """
        # format the SPARQL query into a single line for parsing
        sparql = " ".join(line.strip() for line in sparql.splitlines())

        # transform all letters to lower cases.
        sparqll = sparql.lower()

        # find all variables in the SPARQL between the SELECT and WHERE clause.
        select_start = sparqll.find("select ") + 7
        select_end = sparqll.find(" where", select_start)
        variables = sparql[select_start:select_end].split()

        # find all triples between "WHERE {" and "}"
        where_start = sparqll.find("{", select_end) + 1
        where_end = sparqll.rfind("}", where_start)
        where_text = sparql[where_start:where_end]
        triple_texts = where_text.split(".")
        triples = []
        for triple_text in triple_texts:
            subj, pred, obj = triple_text.strip().split(" ", 2)
            triples.append((subj, pred, obj))

        # find the (optional) ORDER BY clause
        order_by_start = sparqll.find(" order by ", where_end)
        if order_by_start > 0:
            search = sparqll[order_by_start + 10:]
            match = re.search(r"^(asc|desc)\((\?[^\s]+)\)", search)
            assert match is not None, \
                f"could not find order by direction or variable in {search}"
            order_by = (match.group(2).strip(), match.group(1) == "asc")
            assert order_by[0] in variables, \
                f"cannot order by, {order_by[0]} not in variables"
            order_by_end = order_by_start + 10 + len(match.group(0))
        else:
            order_by = None
            order_by_end = where_end

        # find the (optional) LIMIT clause
        limit_start = sparqll.find(" limit ", order_by_end)
        if limit_start > 0:
            limit = int(sparql[limit_start + 7:].split()[0])
        else:
            limit = None

        return variables, triples, order_by, limit

    def sparql_to_sql(self, sparql: str) -> str:
        """

        Translates the given SPARQL query to a corresponding SQL query.

        PLEASE NOTE: there are many ways to express the same SPARQL query in
        SQL. Stick to the implementation advice given in the lecture. Thus, in
        case your formatting, the name of your variables / columns or the
        ordering differs, feel free to adjust the syntax
        (but not the semantics) of the test case.

        The SPARQL query in the test below lists all german politicians whose
        spouses were born in the same birthplace.

        >>> engine = SPARQL()
        >>> engine.sparql_to_sql(
        ...     "SELECT ?x ?y WHERE {"
        ...     "?x occupation politician . "
        ...     "?x country_of_citizenship Germany . "
        ...     "?x spouse ?y . "
        ...     "?x place_of_birth ?z . "
        ...     "?y place_of_birth ?z "
        ...     "}"
        ... ) # doctest: +NORMALIZE_WHITESPACE
        'SELECT t0.subject, \
                t2.object \
         FROM   wikidata as t0, \
                wikidata as t1, \
                wikidata as t2, \
                wikidata as t3, \
                wikidata as t4 \
         WHERE  t0.object="politician" \
                AND t0.predicate="occupation" \
                AND t1.object="Germany" \
                AND t1.predicate="country_of_citizenship" \
                AND t2.predicate="spouse" \
                AND t3.predicate="place_of_birth" \
                AND t3.subject=t0.subject \
                AND t3.subject=t1.subject \
                AND t3.subject=t2.subject \
                AND t4.object=t3.object \
                AND t4.predicate="place_of_birth" \
                AND t4.subject=t2.object;'
        """
        # parse the SPARQL query into its components, might raise an exception
        # if the query is invalid
        variables, triples, order_by, limit = self.parse_sparql(sparql)

        # TODO: compose the SQL query

        select_list = []
        from_list = []
        where_list = []

        var_to_occurrence = {}

        for i, triple in enumerate(triples):
            from_list.append(f"wikidata as t{i}")
            subject = triple[0]
            predicate = triple[1]
            obj = triple[2]

            if subject[0] == "?":
                if subject not in var_to_occurrence:
                    var_to_occurrence[subject] = []
                var_to_occurrence[subject].append(f"t{i}.subject")
            else:
                where_list.append(f"t{i}.subject=\"{subject}\"")

            if obj[0] == "?":
                if obj not in var_to_occurrence:
                    var_to_occurrence[obj] = []
                var_to_occurrence[obj].append(f"t{i}.object")
            else:
                where_list.append(f"t{i}.object=\"{obj}\"")

            where_list.append(f"t{i}.predicate=\"{predicate}\"")


        for var, occurrence in var_to_occurrence.items():

            if len(occurrence) > 1:
                c1 = occurrence[-1]
                for c2 in occurrence[:-1]:
                    where_list.append(f"{c1}={c2}")

            # for c1, c2 in zip(occurrence, occurrence[1:]):
            #     where_list.append(f"{c1}={c2}")

            if var in variables:
                select_list.append(occurrence[0])

        sql_query = ("SELECT " + ", ".join(select_list) + " FROM " + ", ".join(from_list) + " WHERE " + " AND ".join(where_list))

        if order_by:
            order_by_str = var_to_occurrence[order_by[0]][0] + " " + ("ASC" if order_by[1] else "DESC")
            sql_query += " ORDER BY " + order_by_str
        if limit:
            sql_query += " LIMIT " + str(limit)

        sql_query += ";"

        return sql_query



    def process_sql_query(
        self,
        db_name: str,
        sql: str
    ) -> list[tuple[str, ...]]:
        """

        Runs the given SQL query against the given instance of a SQLite3
        database and returns the result rows.

        >>> engine = SPARQL()
        >>> sql = engine.sparql_to_sql(
        ...     "SELECT ?x ?y WHERE {"
        ...     "?x occupation politician . "
        ...     "?x country_of_citizenship Germany . "
        ...     "?x spouse ?y . "
        ...     "?x place_of_birth ?z . "
        ...     "?y place_of_birth ?z "
        ...     "}"
        ... )
        >>> sorted(engine.process_sql_query("example.db", sql))
        ... # doctest: +NORMALIZE_WHITESPACE
        [('Fritz_Kuhn', 'Waltraud_Ulshöfer'), \
         ('Helmut_Schmidt', 'Loki_Schmidt'), \
         ('Karl-Theodor_zu_Guttenberg', 'Stephanie_zu_Guttenberg'), \
         ('Konrad_Adenauer', 'Auguste_Adenauer'), \
         ('Konrad_Adenauer', 'Emma_Adenauer'), \
         ('Konrad_Naumann', 'Vera_Oelschlegel'), \
         ('Waltraud_Ulshöfer', 'Fritz_Kuhn'), \
         ('Wolfgang_Schäuble', 'Ingeborg_Schäuble')]
        """
        # TODO: query the SQLite3 database with the given SQL query

        db = sqlite3.connect(db_name)
        cursor = db.cursor()
        cursor.execute(sql)
        return cursor.fetchall()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "db",
        type=str,
        help="path to the SQLite3 database file"
    )
    parser.add_argument(
        "query",
        type=str,
        help="path to the file containing the SPARQL query"
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    # create a SPARQL engine
    engine = SPARQL()

    # load SPARQL query from file
    with open(args.query, "r", encoding="utf8") as qf:
        sparql = qf.read().strip()

    print(f"\nSPARQL query:\n\n{sparql}")

    try:
        sql = engine.sparql_to_sql(sparql)
    except Exception:
        print("\nInvalid SPARQL query\n")
        return

    # TODO: run the SQL query against the database
    # and print the result rows

    result_rows = engine.process_sql_query(args.db, sql)
    [print(row) for row in result_rows]


if __name__ == "__main__":
    main(parse_args())