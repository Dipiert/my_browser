from unittest import TestCase
import tempfile
from schemas.file.file import FileRequester


class FileSchema(TestCase):

    def test_get_host_and_path(self):
        with tempfile.NamedTemporaryFile(mode="w") as temp_file:
            temp_file_name = temp_file.name
            file_requester = FileRequester(f"file://{temp_file_name}")
            host, path = file_requester.url_parser.get_host_and_path()
            self.assertEqual("localhost", host)
            self.assertEqual(temp_file_name, path)

    def test_get_header_and_body(self):
        with tempfile.NamedTemporaryFile(mode="r+") as temp_file:
            temp_file_name = temp_file.name
            temp_file.write("Hello, world!\n")
            temp_file.seek(0)

            file_requester = FileRequester(f"file://{temp_file_name}")
            header, body = file_requester.get_header_and_body()
            # print()
