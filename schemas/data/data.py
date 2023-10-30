import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class DataRequester:
    """
    Class to handler RFC 2397 - Data scheme.
    """

    def __init__(self, url):
        self.url = url

    def get_header_and_body(self) -> Tuple[None, str]:
        """
        As per RFC 2397 -> data:[<media type>][;base64],<data>
        """
        return None, self.url.split(",", 1)[1]
