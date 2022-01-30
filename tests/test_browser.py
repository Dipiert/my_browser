from unittest import TestCase
from browser import HTTPURL


class HTTPURLTest(TestCase):
    """
    Tests for HTTP schema handler
    """
    def setUp(self) -> None:
        self.http_test = HTTPURL()

    def test_get_host_and_path(self):
        url = "http://example.org/"
        host, path = self.http_test.get_host_and_path(url)
        self.assertEqual(host, 'example.org')
        self.assertEqual(path, '/')

    def test_get_header_and_body(self):
        host = "example.org"
        path = "/"
        headers, body = self.http_test.get_header_and_body(host, path)
        # It seems like there is not such a thing as mandatory header fields:
        # https://stackoverflow.com/a/25586633/5148492
        self.assertTrue(headers)
        self.assertTrue("<title>Example Domain</title>" in body)
