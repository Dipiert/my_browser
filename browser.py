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

import sys
import os
from typing import Tuple
import constants

from schemas.data.data import DataRequester
from schemas.file.file import FileRequester
from schemas.http.http import HTTPRequester, HTTPSRequester


class Browser:

    def request(self, url: str) -> Tuple:
        url_requester = None
        if url.startswith(constants.Schemes.DATA.value):
            url_requester = DataRequester(url)
        elif url.startswith(constants.Schemes.FILE.value):
            url_requester = FileRequester(url)
        elif url.startswith(constants.Schemes.HTTPS.value):
            url_requester = HTTPSRequester(url)
        elif url.startswith(constants.Schemes.HTTP.value):
            url_requester = HTTPRequester(url)

        if not url_requester:
            raise ValueError(f"Unknown scheme in url: {url}")
        return url_requester.get_header_and_body()

    def show(self, body: str) -> None:
        in_angle = False
        for c in body:
            if c == "<":
                in_angle = True
            elif c == ">":
                in_angle = False
            elif not in_angle:
                print(c, end="")

    def load(self, url: str) -> None:
        _, body = self.request(url)
        self.show(body)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S %Z'
    )
    try:
        input_url = sys.argv[1]
    except IndexError:
        input_url = constants.Schemes.FILE.value\
              + "://"\
              + os.path.join("D:\\", "test_browser.txt")

    browser = Browser()
    browser.load(input_url)
