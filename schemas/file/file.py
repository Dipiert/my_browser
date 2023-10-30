import logging
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class FileURLHandler:

    def __init__(self, url):
        self.url = url
        self.host, self.path = self.get_host_and_path()

    def get_host_and_path(self) -> Tuple[str, str]:
        path = self.url.split("://", 1)[1]

        logger.info("Running in localhost")
        logger.info("Path as per URL: %s", path)

        return "localhost", path


class FileRequester:
    """
    Class to handle File schemas
    """

    def __init__(self, url):
        self.url_parser = FileURLHandler(url)

    def get_header_and_body(self) -> Tuple[None, list]:
        logger.info("Opening %s", self.url_parser.url)
        with open(self.url_parser.path, encoding='utf-8') as f:
            return None, f.readlines()