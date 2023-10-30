from unittest import TestCase
from schemas.data.data import DataRequester


class DataSchema(TestCase):

    def test_load(self):
        data_requester = DataRequester("data:text/html,Hello world!")
        header, body = data_requester.get_header_and_body()
        self.assertIsNone(header)
        self.assertEqual(body, "Hello world!")