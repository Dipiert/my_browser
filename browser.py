import logging
import socket
import ssl
import sys

logger = logging.getLogger("browser.py")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class FileURL:

    def __init__(self, path):
        self.path = path


def _handle_input(url, scheme):
    host, path = url.split("/", 1)  # TODO: It requires a "/" as a last char
    path = "/" + path
    logger.info(f"Host: {host}")
    logger.info(f"Path: {path}")
    return host, path


def _get_headers(response):
    headers = {}
    while True:
        line = response.readline()
        if line == "\r\n":
            return headers
        header, value = line.split(":", 1)
        headers[header.lower()] = value.strip()


def _make_request(path, host):
    lines = []
    lines.append(f"GET {path} HTTP/1.1\r\n".encode("utf8"))
    lines.append(f"Host: {host}\r\n".encode("utf8"))
    lines.append(f"Connection: close\r\n".encode("utf8"))
    lines.append(f"User-Agent: dipiert's browser\r\n\r\n".encode("utf8"))
    return b''.join(lines)


def request(url):

    s = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP
    )

    scheme, url = url.split("://", 1)

    # TODO: Use polimorphism for  different schemes
    assert scheme in ["http", "https", "file"], \
        "Unknown scheme {}".format(scheme)

    host, path = _handle_input(url, scheme)
    port = 80

    if scheme == "file":
        file_url = FileURL(url)
        with open(file_url) as f:
            print(f.readlines())

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    if scheme == "https":
        port = 443
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=host)

    s.connect((host, port))

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


def show(body):
    in_angle = False
    for c in body:
        if c == "<":
            in_angle = True
        elif c == ">":
            in_angle = False
        elif not in_angle:
            print(c, end="")


def load(url):
    headers, body = request(url)
    show(body)


if __name__ == '__main__':
    try:
        url = sys.argv[1]
    except IndexError:
        url = "file://D:\\test_browser.txt/"
    load(url)
