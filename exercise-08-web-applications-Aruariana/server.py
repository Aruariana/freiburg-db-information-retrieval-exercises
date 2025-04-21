"""
Copyright 2023, University of Freiburg
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
Natalie Prange <prange@cs.uni-freiburg.de>
Sebastian Walter <swalter@cs.uni-freiburg.de>
"""

import argparse
# import readline  # noqa
import socket
import time
import os

try:
    # try to import the ad_freiburg_qgram_utils package,
    # which contains a faster Rust-based implementation of a q-gram index;
    # install it via pip install ad-freiburg-qgram-utils
    from ad_freiburg_qgram_utils import QGramIndex  # type: ignore
except ImportError:
    # fallback to the Python implementation in qgram_index.py
    # if ad_freiburg_qgram_utils is not installed
    from qgram_index import QGramIndex  # type: ignore


class Server:
    """

    A HTTP server using a q-gram index and SPARQL engine (optional).

    No pre-defined tests are required this time. However, if you add new
    non-trivial methods, you should of course write tests for them.

    Your server should behave like explained in the lecture. For a given
    URL of the form http://<host>:<port>/search.html?q=<query>, your server
    should return a (static) HTML page that displays (1) an input field and a
    search button as shown in the lecture, (2) the query without any URL
    encoding characters and (3) the top-5 entities returned by a q-gram
    index for the query.

    In the following, you will find some example URLs, each given with the
    expected query (%QUERY%) and the expected entities (%RESULT%, each in the
    format "<name>;<score>;<description>") that should be displayed by the
    HTML page returned by your server when calling the URL. Note that, as
    usual, the contents of the test cases is important, but not the exact
    syntax. In particular, there is no HTML markup given, as the layout of
    the HTML pages and the presentation of the entities is up to you. Please
    make sure that the HTML page displays at least the given query and the
    names, scores and descriptions of the given entities in the given order
    (descending sorted by scores).

     URL:
      http://<host>:<port>/search.html?q=angel
     RESPONSE:
      %QUERY%:
        angel
      %RESULT%:
       ["Angela Merkel;211;chancellor of Germany from 2005 to 2021",
        "Angelina Jolie;160;American actress (born 1975)",
        "angel;147;supernatural being or spirit in certain religions and\
                mythologies",
        "Angel Falls;91;waterfall in Venezuela; highest uninterrupted \
                waterfall in the world",
        "Angela Davis;73;American political activist, scholar, and author"
       ]

     URL:
      http://<host>:<port>/search.html?q=eyjaffjala
     RESPONSE:
      %QUERY%:
        eyjaffjala
      %RESULT%:
       ["Eyjafjallajökull;77;ice cap in Iceland covering the caldera of a \
                volcano",
        "Eyjafjallajökull;24;volcano in Iceland",
        "Eyjafjallajökull;8;2013 film by Alexandre Coffre"
       ]

     URL:
      http://<host>:<port>/search.html?q=The+hitschheiker+guide
     RESPONSE:
      %QUERY%:
       The hitschheiker guide
      %RESULT%:
       ["The Hitchhiker's Guide to the Galaxy pentalogy;45;1979-1992 series\
                of five books by Douglas Adams",
        "The Hitchhiker's Guide to the Galaxy;43;1979 book by Douglas Adams",
        "The Hitchhiker's Guide to the Galaxy;37;2005 film directed by Garth \
                Jennings",
        "The Hitchhiker's Guide to the Galaxy;8;1984 interactive fiction video\
                game",
        "The Hitchhiker's Guide to the Galaxy;8;BBC television series"
       ]
    """

    def __init__(
        self,
        port: int,
        qi: QGramIndex,
        db: str | None
    ) -> None:
        """

        Initializes a simple HTTP server with
        the given q-gram index and port.

        Using the database is optional (see task 4).

        """
        self.port = port
        self.qi = qi
        self.db = db

    def run(self) -> None:
        """

        Runs the server loop:
        Creates a socket, and then, in an infinite loop,
        waits for requests and processes them.

        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind(("0.0.0.0", self.port))
        sock.listen(1)

        # TODO: add your code here

        while True:
            # Wait for connection
            connection, address = sock.accept()
            print(f"Connection from {address}")

            # Read request
            request = b""
            while request.find(b"\r\n\r\n") == -1:
                request += connection.recv(1024)

            # Clean request
            request = request.decode("utf-8")
            request = request.split("\r\n")[0]
            request = request.split(" ")[1]
            request = request.replace("/", "")

            response = self.handle_request(request)

            connection.sendall(response)

            connection.close()


    def handle_request(self, request):

        query = ""
        pos = request.find("?query=")
        if pos != -1:
            filename = request[:pos]
            query = request[pos + len("?query="):]
        else:
            filename = request

        status_code = "200 OK"
        media_type = "text/plain"

        response = ""

        server_root = os.getcwd()
        requested_path = os.path.abspath(filename)

        if not os.path.exists(requested_path):
            response = f"File {filename} was not found."
            status_code = "404 NOT FOUND"
        elif not requested_path.startswith(server_root):
            response = "Access to the requested file denied."
            status_code = "403 FORBIDDEN"
        else:
            try:
                with open(filename, "r") as file:
                    response = file.read()
                    if query == "":
                        response = response.replace("%QUERY%", f"<p id=\"query\">Query: </p>")
                        response = response.replace("%RESULT%", f"<p id=\"result\">Results: <br><br> </p>")
                    else:
                        # Cleaning the url
                        query = query.replace("+", " ")

                        # Get the top 5 results in the wanted format here

                        delta = int(len(query) / (self.qi.q + 1))
                        postings = self.qi.find_matches(query, delta)

                        posting_string = ""
                        for syn_id, pedist in postings[:5]:
                            infos = self.qi.get_infos(syn_id)
                            syn, name, score, info = infos
                            posting_string += f"{name} (Score: {score})<br>{info[1]}<br><br>"

                        response = response.replace("%QUERY%", f"<p id=\"query\">Query: {query}</p>")
                        response = response.replace("%RESULT%", f"<p id=\"result\">Results: <br><br> {posting_string}</p>")

                    if filename.endswith(".html"):
                        media_type = "text/html"
                    if filename.endswith(".css"):
                        media_type = "text/css"
            except FileNotFoundError:
                response = f"File {filename} was not found."
                status_code = "404 NOT FOUND"

        response += "\r\n"

        headers = f"HTTP/1.1 {status_code}\r\n"
        headers += f"Content-Length: {len(response)}\r\n"
        headers += f"Content-Type: {media_type}\r\n"
        headers += f"Connection: close\r\n"
        headers += f"\r\n\r\n"

        return (headers + response).encode("utf-8")



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "entities",
        type=str,
        help="path to entities file for q-gram index"
    )
    parser.add_argument(
        "port",
        type=int,
        help="port to run the server on"
    )
    parser.add_argument(
        "-q",
        "--q-grams",
        type=int,
        default=3,
        help="size of the q-grams"
    )
    parser.add_argument(
        "-db",
        "--database",
        type=str,
        default=None,
        help="path to sqlite3 database for SPARQL engine"
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

    Builds a q-gram index from the given file
    and starts a server on the given port.

    """
    # Create a new q-gram index from the given file.
    print(f"Building q-gram index from file {args.entities}.")
    start = time.perf_counter()
    q = QGramIndex(args.q_grams, args.use_synonyms)
    q.build_from_file(args.entities)
    print(f"Done, took {(time.perf_counter() - start) * 1000:.1f}ms.")

    server = Server(
        args.port,
        q,
        args.database
    )
    print(
        f"Starting server on port {args.port}, go to "
        f"http://localhost:{args.port}/search.html"
    )
    server.run()


if __name__ == "__main__":
    main(parse_args())