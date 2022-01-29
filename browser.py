"""
Main file for my_browser

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

import logging
import socket
import ssl
import sys
import os
from typing import Tuple, Dict
from typing.io import TextIO

import constants


logger = logging.getLogger("browser.py")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class HTTPSURL:
    """
    Class which handles HTTPS Schema
    """
    def __init__(self):
        self.port = 443

    @staticmethod
    def get_host_and_path(url: str) -> Tuple[str, str]:
        url = url.split("://", 1)[1]
        host, path = url.split("/", 1)
        path = "/" + path

        logger.info("Host: %s", host)
        logger.info("Path: %s", path)

        return host, path

    def get_header_and_body(self, host: str, path: str) -> Tuple[Dict, str]:
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        if ":" in host:
            host, port = host.split(":", 1)
            logger.info("Setting port to %s", port)

        s = ssl.create_default_context().wrap_socket(s, server_hostname=host)

        # Below is common between HTTP and HTTPS:
        s.connect((host, self.port))

        return_code = s.send(_make_request(path, host))
        logger.info("Bytes sent by socket: %s", return_code)
        response = s.makefile(
            "r",
            encoding="utf8",
            newline="\r\n"
        )
        statusline = response.readline()
        _, status, explanation = statusline.split(" ", 2)
        assert status == "200", f"{status}: {explanation}"
        headers = _get_headers(response)
        body = response.read()
        s.close()
        return headers, body


class HTTPURL:
    """
    Class that handles HTTP Schema
    """

    def __init__(self):
        self.port = 80

    @staticmethod
    def get_host_and_path(url: str) -> Tuple[str, str]:
        url = url.split("://", 1)[1]
        host, path = url.split("/", 1)
        path = "/" + path

        logger.info("Host: %s", host)
        logger.info("Path: %s", path)

        return host, path

    def get_header_and_body(self, host: str, path: str) -> Tuple[Dict, str]:
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        if ":" in host:
            host, port = host.split(":", 1)
            logger.info("Setting port to %s", port)
            self.port = int(port)

        s.connect((host, self.port))

        # Below is common between HTTP and HTTPS:
        return_code = s.send(_make_request(path, host))
        logger.info("Bytes sent by socket: %s", return_code)
        response = s.makefile(
            "r",
            encoding="utf8",
            newline="\r\n"
        )
        statusline = response.readline()
        _, status, explanation = statusline.split(" ", 2)
        assert status == "200", f"{status}: {explanation}"
        headers = _get_headers(response)
        body = response.read()
        s.close()
        return headers, body


class DataURL:
    """
    Class to handler RFC 2397 - Data scheme.
    """

    @staticmethod
    def get_host_and_path(url):
        host = "localhost"
        path = url

        logger.info("Host: %s", host)
        logger.info("Path: %s", path)

        return host, path

    @staticmethod
    def get_header_and_body(_: str, url: str) -> Tuple[None, str]:
        """
        As per RFC 2397 -> data:[<media type>][;base64],<data>
        """
        return None, url.split(",", 1)[1]


class FileURL:
    """
    Class to handle File schemas
    """

    @staticmethod
    def get_host_and_path(url: str) -> Tuple[str, str]:
        host = "localhost"
        path = url.split("://", 1)[1]

        logger.info("Host: %s", host)
        logger.info("Path: %s", path)

        return host, path

    @staticmethod
    def get_header_and_body(_: str, url: str) -> Tuple[None, list]:
        logger.info("Opening %s", url)
        with open(url, encoding='utf-8') as f:
            return None, f.readlines()


def get_host_and_path(url: str) -> Tuple[str, str]:
    host, path = url.split("/", 1)
    path = "/" + path

    logger.info("Host: %s", host)
    logger.info("Path: %s", path)

    return host, path


def _get_headers(response: TextIO) -> Dict:
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
        "Connection: close\r\n".encode("utf8"),
        "User-Agent: dipiert's browser\r\n\r\n".encode("utf8")
    ]
    return b''.join(lines)


def request(url: str) -> Tuple:
    url_parser = None
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
    _, body = request(url)
    show(body)


if __name__ == '__main__':
    try:
        input_url = sys.argv[1]
    except IndexError:
        input_url = constants.Schemes.FILE.value\
              + "://"\
              + os.path.join("D:\\", "test_browser.txt")
    load(input_url)
