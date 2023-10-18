import os
from pathlib import Path

import mock
from django.test import TestCase

from frontend.utils.vector_tile import convert_size, get_folder_size


class TestVectorTileUtils(TestCase):
    """
    Test Vector tile utils.
    """

    def setUp(self) -> None:
        dirname = os.path.dirname(__file__)
        self.dir_path = Path(os.path.join(dirname, 'csv'))

    def test_convert_size_byte(self):
        converted_size = convert_size(512)
        self.assertEqual(converted_size, '512.0 B')

    def test_convert_size_kilobyte(self):
        converted_size = convert_size(1024)
        self.assertEqual(converted_size, '1.0 KB')

    def test_convert_size_megabyte(self):
        converted_size = convert_size(1024 ** 2)
        self.assertEqual(converted_size, '1.0 MB')

    def test_convert_size_gigabyte(self):
        converted_size = convert_size(1024 ** 3)
        self.assertEqual(converted_size, '1.0 GB')

    def test_convert_size_terabyte(self):
        converted_size = convert_size(1024 ** 4)
        self.assertEqual(converted_size, '1.0 TB')

    @mock.patch('frontend.utils.vector_tile.get_folder_size')
    def test_get_folder_size(self, mock_folder_size):
        size = get_folder_size(self.dir_path)

        mock_folder_size.return_value = size
