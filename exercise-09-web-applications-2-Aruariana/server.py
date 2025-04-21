"""
Copyright 2023, University of Freiburg
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Patrick Brosi <brosi@cs.uni-freiburg.de>
Natalie Prange <prange@cs.uni-freiburg.de>
Sebastian Walter <swalter@cs.uni-freiburg.de>
"""

import argparse
import os
# import readline  # noqa
import socket
import time

from sparql_to_sql import SPARQL
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

    A HTTP server using a q-gram index and SPARQL engine.

    In the following, you will find some example URLs for the search
    and relations APIs, each given with the expected JSON output.
    Note that, as usual, the contents of the test cases is important,
    but not the exact syntax.

    URL:
      http://<host>:<port>/api/search?q=angel
    RESPONSE:
      {
        "numTotalResults": 2152,
        "results": [
          {
            "name": "Angela Merkel",
            "score": 211,
            "description": "chancellor of Germany from 2005 to 2021"
          },
          {
            "name": "Angelina Jolie",
            "score": 160,
            "description": "American actress (born 1975)"
          },
          {
            "name": "angel",
            "score": 147,
            "description": "supernatural being or spirit in certain religions \
            and mythologies"
          },
          {
            "name": "Angel Falls",
            "score": 91,
            "description": "waterfall in Venezuela; \
            highest uninterrupted waterfall in the world"
          },
          {
            "name": "Angela Davis",
            "score": 73,
            "description": "American political activist, scholar, and author"
          }
        ]
      }

    URL:
      http://<host>:<port>/api/search?q=eyj%C3%A4fja
    RESPONSE:
      {
        "numTotalResults": 4,
        "results": [
          {
            "name": "Eyjafjallajökull",
            "score": 77,
            "description": "ice cap in Iceland covering the caldera of a \
            volcano"
          },
          {
            "name": "Eyjafjallajökull",
            "score": 24,
            "description": "volcano in Iceland"
          },
          {
            "name": "Eyjafjarðarsveit",
            "score": 21,
            "description": "municipality of Iceland"
          },
          {
            "name": "Eyjafjallajökull",
            "score": 8,
            "description": "2013 film by Alexandre Coffre"
          }
        ]
      }

    URL:
      http://<host>:<port>/api/relations?id=Q567
    RESPONSE:
      [
        {
            "predicate" : "instance of",
            "object": "human"
        },
        {
            "predicate" : "occupation",
            "object": "physicist, politician"
        },
        {
            "predicate" : "sex or gender",
            "object": "female"
        },
        {
            "predicate" : "given name",
            "object": "Angela"
        },
        {
            "predicate" : "country of citizenship",
            "object": "Germany"
        },
        {
            "predicate" : "place of birth",
            "object": "Eimsbüttel"
        },
        {
            "predicate" : "languages spoken, written or signed",
            "object": "German"
        },
        {
            "predicate" : "educated at",
            "object": "Leipzig University, Academy of Sciences of the GDR"
        },
        {
            "predicate" : "award received",
            "object": "Jawaharlal Nehru Award for International Understanding,\
            Order of Stara Planina, Robert Schuman Medal, Order of the \
            Republic, Order of Zayed, Bavarian Order of Merit, Order of Merit \
            of the Italian Republic, Order of King Abdulaziz al Saud, Order \
            of Vytautas the Great, Félix Houphouët-Boigny Peace Prize, \
            Order of Liberty, Order of the Three Stars, Presidential Medal of \
            Distinction, Supreme Order of the Renaissance, Time Person of the \
            Year, Nansen Refugee Award, Financial Times Person of the Year, \
            Charlemagne Prize, Presidential Medal of Freedom"
        },
        {
            "predicate" : "position held",
            "object": "Federal Chancellor of Germany"
        },
        {
            "predicate" : "father",
            "object": "Horst Kasner"
        },
        {
            "predicate" : "field of work",
            "object": "analytical chemistry, theoretical chemistry, \
            politics, physics"
        },
        {
            "predicate" : "participant in",
            "object": "2012 German presidential election, 2009 German \
            presidential election, 2017 German presidential election, \
            2010 German presidential election"
        },
        {
            "predicate" : "spouse",
            "object": "Joachim Sauer"
        },
        {
            "predicate" : "topic's main category",
            "object": "Category:Angela Merkel"
        },
        {
            "predicate" : "member of",
            "object": "Fourth Merkel cabinet, Third Merkel cabinet, Cabinet \
            Kohl IV, Cabinet Kohl V, Free German Youth, First Merkel cabinet, \
            Second Merkel cabinet"
        }
      ]

    URL:
      http://<host>:<port>/api/relations?id=Q39651
    RESPONSE:
      [
        {
            "predicate" : "instance of",
            "object": "ice cap"
        },
        {
            "predicate" : "country",
            "object": "Iceland"
        },
        {
            "predicate" : "located in the administrative territorial entity",
            "object": "Rangárþing eystra, Southern Region"
        },
        {
            "predicate" : "located in time zone",
            "object": "UTC±00:00"
        },
        {
            "predicate" : "different from",
            "object": "Eyjafjallajökull"
        },
        {
            "predicate" : "topic's main category",
            "object": "Category:Eyjafjallajökull"
        }
      ]
    """

    def __init__(
        self,
        port: int,
        qi: QGramIndex,
        db: str,
        party_pooper: bool = False
    ) -> None:
        """

        Initializes a simple HTTP server with
        the given q-gram index, database and port.

        """
        self.port = port
        self.qi = qi
        self.db = db
        self.engine = SPARQL()
        self.party_pooper = party_pooper

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
            request = request[1:]

            response = self.handle_request(request)

            print(response)
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

        if filename == "api/search":
            if query == "":
                response = "API called with empty query."
            else:
                # Cleaning the url
                query = self.url_decode(query)

                # Get the top 5 results in the wanted format here
                delta = int(len(query) / (self.qi.q + 1))
                postings = self.qi.find_matches(query, delta)

                response = f"{{ \"numTotalResults\" : \"{len(postings)}\", \"results\" : "

                posting_json_list = []
                for syn_id, pedist in postings[:5]:
                    infos = self.qi.get_infos(syn_id)
                    syn, name, score, info = infos
                    posting_json_list.append(f"{{ \"name\" : \"{name}\", \"score\" : \"{score}\", \"description\" : \"{info[1]}\" }}")
                response += "[" + " , ".join(posting_json_list) + "]" + "}"
                media_type = "application/json"

        else:
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
                            query = self.url_decode(query)

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

        response += "\r\n\r\n"
        response = response.encode("utf-8")

        headers = f"HTTP/1.1 {status_code}\r\n"
        headers += f"Content-Length: {len(response)}\r\n"
        headers += f"Content-Type: {media_type}\r\n"
        # headers += f"Connection: close\r\n"
        headers += f"\r\n\r\n"
        headers = headers.encode("utf-8")

        return headers + response

    def url_decode(self, string: str) -> str:
        """

        Decodes an URL-encoded UTF-8 string, as explained in the lecture.
        Also decodes "+" to " " (space).

        >>> s = Server(0, None, "")
        >>> s.url_decode("nirwana")
        'nirwana'
        >>> s.url_decode("the+m%C3%A4trix")
        'the mätrix'
        >>> s.url_decode("Mikr%C3%B6soft+Windos")
        'Mikrösoft Windos'
        >>> s.url_decode("The+hitschheiker%20guide")
        'The hitschheiker guide'
        """
        # TODO: add your code here

        result = b""

        idx = 0
        while idx < len(string):
            ch = string[idx]
            if ch == "+":
                result += b" "
                idx += 1
            elif ch == "%":
                hex_code = string[idx+1:idx+3]
                result += bytes.fromhex(hex_code)
                idx += 3
            else:
                result += string[idx].encode("utf8")
                idx += 1

        return result.decode("utf8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "entities",
        type=str,
        help="path to entities file for q-gram index"
    )
    parser.add_argument(
        "db",
        type=str,
        help="path to sqlite3 database for SPARQL engine"
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
        "-s",
        "--use-synonyms",
        action="store_true",
        help="whether to use synonyms for the q-gram index"
    )
    parser.add_argument(
        "-p",
        "--party-pooper",
        action="store_true",
        help="whether to prevent code injection"
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    # Create a new q-gram index from the given file.
    print(f"Building q-gram index from file {args.entities}.")
    start = time.perf_counter()
    q = QGramIndex(args.q_grams, args.use_synonyms)
    q.build_from_file(args.entities)
    print(f"Done, took {(time.perf_counter() - start) * 1000:.1f}ms.")

    server = Server(
        args.port,
        q,
        args.db,
        args.party_pooper
    )
    print(
        f"Starting server on port {args.port}, go to "
        f"http://localhost:{args.port}/search.html"
    )
    server.run()


if __name__ == "__main__":
    main(parse_args())
