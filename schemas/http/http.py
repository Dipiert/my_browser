import logging
from typing import Tuple, Dict, TextIO
import socket
import ssl

logger = logging.getLogger(__name__)


class BaseHTTPURLParser:
    def __init__(self, url):
        self.url = url
        self.host, self.path, self.port = self.get_host_and_path_and_port()

    def get_host_and_path_and_port(self) -> Tuple[str, str]:
        url = self.url.split("://", 1)[1]
        host_and_port, path = url.split("/", 1)

        if ":" in host_and_port:
            host, port = host_and_port.split(":", 1)
            port = int(port)
        else:
            host, port = host_and_port, None

        path = "/" + path

        logger.info("Host as per URL: %s", host)
        logger.info("Path as per URL: %s", path)
        logger.info("Port as per URL: %s", port)
        return host, path, port


class BaseHTTPRequester:

    def __init__(self, url):
        self.url_parser = BaseHTTPURLParser(url)
        self.my_socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

    def get_header_and_body(self) -> Tuple[Dict, str]:
        self.my_socket.connect((self.url_parser.host, self.url_parser.port))
        return_code = self.my_socket.send(self._make_request(self.url_parser.path, self.url_parser.host))
        logger.info("Bytes sent by socket: %s", return_code)
        response = self.my_socket.makefile(
            "r",
            encoding="utf8",
            newline="\r\n"
        )
        statusline = response.readline()
        _, status, explanation = statusline.split(" ", 2)
        if status != "200":
            raise AssertionError(f"Expected code 200. Got {status}: {explanation}")
        headers = self._get_headers(response)
        body = response.read()
        self.my_socket.close()
        return headers, body

    def _get_headers(self, response: TextIO) -> Dict:
        headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                return headers
            header, value = line.split(":", 1)
            headers[header.lower()] = value.strip()


class HTTPSURLParser(BaseHTTPURLParser):

    def __init__(self, url):
        super().__init__(url)


class HTTPSRequester(BaseHTTPRequester):
    """
    Class which handles HTTPS Schema
    """
    def __init__(self, url):
        super().__init__(url)
        if not self.url_parser.port:
            logger.info("Using default port for HTTPS (443)")
            self.url_parser.port = 443

        self.my_socket = self._wrap_socket_context()

    def _make_request(self, path: str, host: str) -> bytes:
        lines = [
            f"GET {path} HTTP/1.1\r\n".encode("utf8"),
            f"Host: {host}\r\n".encode("utf8"),
            "Connection: close\r\n".encode("utf8"),
            "User-Agent: dipiert's browser\r\n\r\n".encode("utf8")
        ]
        return b''.join(lines)

    def _wrap_socket_context(self):
        return ssl.create_default_context().wrap_socket(
            self.my_socket,
            server_hostname=self.url_parser.host
        )


class HTTPURLParser(BaseHTTPURLParser):
    def __init__(self, url):
        super().__init__(url)


class HTTPRequester(BaseHTTPRequester):
    """
    Class that handles HTTP Schema
    """
    def __init__(self, url):
        super().__init__(url)
        if not self.url_parser.port:
            logger.info("Using default port for HTTP (80)")
            self.url_parser.port = 80

    def _make_request(self, path: str, host: str) -> bytes:
        lines = [
            f"GET {path} HTTP/1.1\r\n".encode("utf8"),
            f"Host: {host}\r\n".encode("utf8"),
            "Connection: close\r\n".encode("utf8"),
            "User-Agent: dipiert's browser\r\n\r\n".encode("utf8")
        ]
        return b''.join(lines)