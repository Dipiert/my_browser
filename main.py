import logging
logger = logging.getLogger("main.py")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

DEFAULT_PORT = 80
DEFAULT_SCHEME = "http://"


def _handle_input(url):
    assert url.startswith(DEFAULT_SCHEME)
    url = url[len(DEFAULT_SCHEME):]
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


def request(url):
    import socket
    s = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP
    )
    host, path = _handle_input(url)
    s.connect((host, DEFAULT_PORT))
    first_line = f"GET {path} HTTP/1.0\r\n".encode("utf8")
    second_line = f"Host: {host}\r\n\r\n".encode("utf8")
    return_code = s.send(first_line+second_line)
    logger.info(f"Bytes sent by socket: {return_code}")
    response = s.makefile("r", encoding="utf8", newline="\r\n")  # TODO: Get encoding from Content-Type
    statusline = response.readline()
    version, status, explanation = statusline.split(" ", 2)
    assert status == "200", "{}: {}".format(status, explanation)
    headers = _get_headers(response)
    body = response.read()
    s.close()
    return headers, body


def main(url):
    headers, body = request(url)
    print(headers)
    print(body)

if __name__ == '__main__':
    main("http://example.org/")
