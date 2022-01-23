import logging
import socket
import ssl
import sys
import os
import constants
from typing import Tuple

logger = logging.getLogger("browser.py")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class HTTPSURL:
    def __init__(self):
        self.port = 443

    @staticmethod
    def get_host_and_path(url: str) -> Tuple[str, str]:
        url = url.split("://", 1)[1]
        host, path = url.split("/", 1)  # TODO: It requires a "/" as a last char
        path = "/" + path

        logger.info(f"Host: {host}")
        logger.info(f"Path: {path}")

        return host, path

    def get_header_and_body(self, host: str, path: str) -> Tuple[str, str]:
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        if ":" in host:
            host, port = host.split(":", 1)
            logger.info(f"Setting port to {port}")
            port = int(port)

        s = ssl.create_default_context().wrap_socket(s, server_hostname=host)

        # Below is common between HTTP and HTTPS:
        s.connect((host, self.port))

        return_code = s.send(_make_request(path, host))
        logger.info(f"Bytes sent by socket: {return_code}")
        response = s.makefile("r", encoding="utf8", newline="\r\n")  # TODO: Get encoding from Content-Type
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        assert status == "200", "{}: {}".format(status, explanation)
        headers = _get_headers(response)
        body = response.read()
        s.close()
        return headers, body


class HTTPURL:

    def __init__(self):
        self.port = 80

    @staticmethod
    def get_host_and_path(url: str) -> Tuple[str, str]:
        url = url.split("://", 1)[1]
        host, path = url.split("/", 1)  # TODO: It requires a "/" as a last char
        path = "/" + path

        logger.info(f"Host: {host}")
        logger.info(f"Path: {path}")

        return host, path

    def get_header_and_body(self, host: str, path: str) -> Tuple[str, str]:
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        if ":" in host:
            host, port = host.split(":", 1)
            logger.info(f"Setting port to {port}")
            self.port = int(port)

        s.connect((host, self.port))

        # Below is common between HTTP and HTTPS:
        return_code = s.send(_make_request(path, host))
        logger.info(f"Bytes sent by socket: {return_code}")
        response = s.makefile("r", encoding="utf8", newline="\r\n")  # TODO: Get encoding from Content-Type
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        assert status == "200", "{}: {}".format(status, explanation)
        headers = _get_headers(response)
        body = response.read()
        s.close()
        return headers, body


class DataURL:

    @staticmethod
    def get_host_and_path(url):
        host = "localhost"
        path = url

        logger.info(f"Host: {host}")
        logger.info(f"Path: {path}")

        return host, path

    def get_header_and_body(self, host: str, path: str) -> Tuple[None, str]:
        """
        As per RFC 2397 -> data:[<media type>][;base64],<data>
        """
        return None, url.split(",", 1)[1]


class FileURL:

    @staticmethod
    def get_host_and_path(url: str) -> Tuple[str, str]:
        host = "localhost"
        path = url.split("://", 1)[1]

        logger.info(f"Host: {host}")
        logger.info(f"Path: {path}")

        return host, path

    def get_header_and_body(self, host: str, url: str) -> Tuple[None, list]:
        logger.info(f"Opening {url}")
        with open(url) as f:
            return None, f.readlines()


def get_host_and_path(url: str) -> Tuple[str, str]:
    host, path = url.split("/", 1)  # TODO: It requires a "/" as a last char
    path = "/" + path

    logger.info(f"Host: {host}")
    logger.info(f"Path: {path}")

    return host, path


def _get_headers(response: str) -> None:
    headers = {}
    while True:
        line = response.readline()
        if line == "\r\n":
            return headers
        header, value = line.split(":", 1)
        headers[header.lower()] = value.strip()


def _make_request(path: str, host: str) -> bytes:
    lines = [
        f"GET {path} HTTP/1.1\r\n".encode("utf8"),
        f"Host: {host}\r\n".encode("utf8"),
        f"Connection: close\r\n".encode("utf8"),
        f"User-Agent: dipiert's browser\r\n\r\n".encode("utf8")
    ]
    return b''.join(lines)


def request(url: str) -> Tuple:
    if url.startswith(constants.Schemes.DATA.value):
        url_parser = DataURL()
    if url.startswith(constants.Schemes.FILE.value):
        url_parser = FileURL()
    if url.startswith(constants.Schemes.HTTPS.value):
        url_parser = HTTPSURL()
    if url.startswith(constants.Schemes.HTTP.value):
        url_parser = HTTPURL()

    if not url_parser:
        raise ValueError(f"Unknown scheme in url: {url}")

    host, path = url_parser.get_host_and_path(url)
    return url_parser.get_header_and_body(host, path)


def show(body: str) -> None:
    in_angle = False
    for c in body:
        if c == "<":
            in_angle = True
        elif c == ">":
            in_angle = False
        elif not in_angle:
            print(c, end="")


def load(url: str) -> None:
    headers, body = request(url)
    show(body)


if __name__ == '__main__':
    """
    Usage examples:
    Data:
       # python3 browser.py "data:text/html,Hello world!"
    File:
       # python3 browser.py file://D:\\test_browser.txt
    HTTP:
       # python3 browser.py http://example.org/
    HTTPS:
       # python3 browser.py https://example.org/
    """
    try:
        url = sys.argv[1]
    except IndexError:
        url = constants.Schemes.FILE.value + "://" + os.path.join("D:\\", "test_browser.txt")
    load(url)
