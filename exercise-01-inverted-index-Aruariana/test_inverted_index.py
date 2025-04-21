from inverted_index import InvertedIndex


def test_build_from_file():
    ii = InvertedIndex()
    ii.build_from_file("example.tsv")
    assert sorted(ii.inverted_lists.items()) == [
                  ('a', [1, 2]), ('doc', [1, 2, 3]), ('film', [2]), ('movie', [1, 3])]
    assert ii.records == [('Doc 1', 'A movie movie.'),
                          ('Doc 2', 'A film.'), ('Doc 3', 'Movie.')]


def test_intersect():
    ii = InvertedIndex()
    assert ii.intersect([1, 5, 7], [2, 4]) == []
    assert ii.intersect([1, 2, 5, 7], [1, 3, 5, 6, 7, 9]) == [1, 5, 7]


def test_process_query():
    ii = InvertedIndex()
    ii.build_from_file("example.tsv")
    assert ii.process_query([]) == []
    assert ii.process_query(["doc"]) == [1, 2, 3]
    assert ii.process_query(["doc", "movie"]) == [1, 3]
    assert ii.process_query(["doc", "movie", "comedy"]) == []
    assert ii.process_query(["comedy"]) == []
