from unittest import TestCase
from browser import HTTPURL


class HTTPURLTest(TestCase):

    def setUp(self) -> None:
        self.http_test = HTTPURL()

    def test_get_host_and_path(self):
        url = "http://example.org/"
        host, path = self.http_test.get_host_and_path(url)
        self.assertEqual(host, 'example.org')
        self.assertEqual(path, '/')

