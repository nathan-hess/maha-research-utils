import unittest

from mahautils.files import File
from tests import SAMPLE_FILES_DIR


class Test_File(unittest.TestCase):
    def setUp(self):
        self.file_str = str(SAMPLE_FILES_DIR / 'general_text_file_001.txt')

        self.file_from_pathlib = File(SAMPLE_FILES_DIR / 'general_text_file_001.txt')
        self.file_from_str = File(self.file_str)

        # Known file hashes
        self.hashes = {
            'md5': 'b8c4707ddd8e71744899222680a08060',
            'sha1': '7baba1d3b8b4ff88995d97c2321a7dca5de91460',
            'sha224': '40769b9535d5ec2a18b37f8b666c198a8b78668f192f1885def71792',
            'sha256': 'cc7d0f19c158e4141585c57e5278320bc60f049e5ec18ec472668660f0d4aaa7',
            'sha384': '11723482eaa0a8cbffc201cc7cd6085fd6beb9f7505fa26f1c223782cf3634ae4bd0bc65d27131f5173ff7519600630c',
            'sha512': 'a8b65a414cba9df08d5fc5f9a476e43d29ef636621011e222830182dc396f4cd4618a49b5e8c21a5dbd8706fe5cd174a118d24969d6d49f614272a2e3841c515',
        }

    def test_file_str(self):
        # Verifies that path and filename is correctly returned
        # as a string
        self.assertEqual(str(self.file_from_pathlib), self.file_str)
        self.assertEqual(str(self.file_from_str), self.file_str)

    def test_file_repr_before(self):
        # Verifies that file object descriptor is computed correctly before
        # computing file hashes
        self.assertEqual(
            self.file_from_pathlib.__repr__(),
            f"<class 'mahautils.files.files.File'>\n--> File: {self.file_str}"
        )

        self.assertEqual(
            self.file_from_str.__repr__(),
            f"<class 'mahautils.files.files.File'>\n--> File: {self.file_str}"
        )

    def test_file_repr_after_single(self):
        # Verifies that file object descriptor is computed correctly after
        # computing file hashes
        self.file_from_pathlib.compute_file_hashes('sha512')
        self.assertEqual(
            self.file_from_pathlib.__repr__(),
            (f"<class 'mahautils.files.files.File'>\n"
             f"--> File: {self.file_str}\n"
             f"--> File hash:\n"
             f"    sha512: {self.hashes['sha512']}")
        )

        self.file_from_str.compute_file_hashes('sha512')
        self.assertEqual(
            self.file_from_str.__repr__(),
            (f"<class 'mahautils.files.files.File'>\n"
             f"--> File: {self.file_str}\n"
             f"--> File hash:\n"
             f"    sha512: {self.hashes['sha512']}")
        )

    def test_file_repr_after_multiple(self):
        # Verifies that file object descriptor is computed correctly after
        # computing file hashes
        self.file_from_pathlib.compute_file_hashes(('md5', 'sha256'))
        self.assertEqual(
            self.file_from_pathlib.__repr__(),
            (f"<class 'mahautils.files.files.File'>\n"
             f"--> File: {self.file_str}\n"
             f"--> File hashes:\n"
             f"    md5: {self.hashes['md5']}\n"
             f"    sha256: {self.hashes['sha256']}")
        )

        self.file_from_str.compute_file_hashes(('md5', 'sha256'))
        self.assertEqual(
            self.file_from_str.__repr__(),
            (f"<class 'mahautils.files.files.File'>\n"
             f"--> File: {self.file_str}\n"
             f"--> File hashes:\n"
             f"    md5: {self.hashes['md5']}\n"
             f"    sha256: {self.hashes['sha256']}")
        )
