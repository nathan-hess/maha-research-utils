import unittest

from mahautils.utils.filetools import compute_file_hash
from tests import SAMPLE_FILES_DIR


class Test_FileHash(unittest.TestCase):
    def setUp(self):
        # File for which to compute hashes
        self.file = SAMPLE_FILES_DIR / 'general_text_file_001.txt'

        # Known file hashes for `self.file`
        self.hashes = {
            'md5': 'b8c4707ddd8e71744899222680a08060',
            'sha1': '7baba1d3b8b4ff88995d97c2321a7dca5de91460',
            'sha224': '40769b9535d5ec2a18b37f8b666c198a8b78668f192f1885def71792',
            'sha256': 'cc7d0f19c158e4141585c57e5278320bc60f049e5ec18ec472668660f0d4aaa7',
            'sha384': '11723482eaa0a8cbffc201cc7cd6085fd6beb9f7505fa26f1c223782cf3634ae4bd0bc65d27131f5173ff7519600630c',
            'sha512': 'a8b65a414cba9df08d5fc5f9a476e43d29ef636621011e222830182dc396f4cd4618a49b5e8c21a5dbd8706fe5cd174a118d24969d6d49f614272a2e3841c515',
        }

    def test_md5(self):
        # Verifies that MD5 hash of a file is computed correctly
        self.assertEqual(compute_file_hash(self.file, 'md5'),   self.hashes['md5'])
        self.assertEqual(compute_file_hash(self.file, 'md_5'),  self.hashes['md5'])
        self.assertEqual(compute_file_hash(self.file, 'MD-5'),  self.hashes['md5'])
        self.assertEqual(compute_file_hash(self.file, 'mD-_5'), self.hashes['md5'])
        self.assertEqual(compute_file_hash(self.file, 'MD5'),   self.hashes['md5'])

    def test_sha1(self):
        # Verifies that SHA-1 hash of a file is computed correctly
        self.assertEqual(compute_file_hash(self.file, 'sha1'), self.hashes['sha1'])
        self.assertEqual(compute_file_hash(self.file, 'sha_1'), self.hashes['sha1'])
        self.assertEqual(compute_file_hash(self.file, 'SHA-1'), self.hashes['sha1'])
        self.assertEqual(compute_file_hash(self.file, 'sHa-_1'), self.hashes['sha1'])

    def test_sha224(self):
        # Verifies that SHA-224 hash of a file is computed correctly
        self.assertEqual(compute_file_hash(self.file, 'sha224'),   self.hashes['sha224'])
        self.assertEqual(compute_file_hash(self.file, 'sha_224'),  self.hashes['sha224'])
        self.assertEqual(compute_file_hash(self.file, 'SHA-224'),  self.hashes['sha224'])
        self.assertEqual(compute_file_hash(self.file, 'sHa-_224'), self.hashes['sha224'])

    def test_sha224(self):
        # Verifies that SHA-224 hash of a file is computed correctly
        self.assertEqual(compute_file_hash(self.file, 'sha224'),   self.hashes['sha224'])
        self.assertEqual(compute_file_hash(self.file, 'sha_224'),  self.hashes['sha224'])
        self.assertEqual(compute_file_hash(self.file, 'SHA-224'),  self.hashes['sha224'])
        self.assertEqual(compute_file_hash(self.file, 'sHa-_224'), self.hashes['sha224'])

    def test_sha384(self):
        # Verifies that SHA-384 hash of a file is computed correctly
        self.assertEqual(compute_file_hash(self.file, 'sha384'),   self.hashes['sha384'])
        self.assertEqual(compute_file_hash(self.file, 'sha_384'),  self.hashes['sha384'])
        self.assertEqual(compute_file_hash(self.file, 'SHA-384'),  self.hashes['sha384'])
        self.assertEqual(compute_file_hash(self.file, 'sHa-_384'), self.hashes['sha384'])

    def test_sha512(self):
        # Verifies that SHA-512 hash of a file is computed correctly
        self.assertEqual(compute_file_hash(self.file, 'sha512'),   self.hashes['sha512'])
        self.assertEqual(compute_file_hash(self.file, 'sha_512'),  self.hashes['sha512'])
        self.assertEqual(compute_file_hash(self.file, 'SHA-512'),  self.hashes['sha512'])
        self.assertEqual(compute_file_hash(self.file, 'sHa-_512'), self.hashes['sha512'])

    def test_hash_default(self):
        # Verifies that hash of a file is computed correctly and equal
        # to the SHA-256 hash using the default `hash_function` argument
        self.assertEqual(compute_file_hash(self.file), self.hashes['sha256'])
