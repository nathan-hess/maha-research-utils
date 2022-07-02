import pathlib
import unittest

from mahautils.dictionary import FileDictionary
from mahautils.dictionary.exceptions import FileDictionaryPathExistsError
from tests import CapturePrint, SAMPLE_FILES_DIR


class Test_FileDict(unittest.TestCase):
    def setUp(self):
        self.filedict = FileDictionary(SAMPLE_FILES_DIR)

        self.filedict_filled_1 = FileDictionary(SAMPLE_FILES_DIR)
        self.filedict_filled_1['file1'] = SAMPLE_FILES_DIR / 'general_text_file_001.txt'
        self.filedict_filled_1['file2'] = 'general_text_file_002.txt'
        self.filedict_filled_1['file3'] = 'nonexistent_file.ipynb'

        self.filedict_filled_2 = FileDictionary(SAMPLE_FILES_DIR)
        self.filedict_filled_2['file1_abs'] = SAMPLE_FILES_DIR / 'general_text_file_001.txt'
        self.filedict_filled_2['file1_rel'] = './general_text_file_001.txt'
        self.filedict_filled_2['file2_abs'] = SAMPLE_FILES_DIR / 'subdirectory_001' / 'sample_subfile_001.txt'
        self.filedict_filled_2['file2_rel'] = './subdirectory_001/sample_subfile_001.txt'
        self.filedict_filled_2['dir1_abs'] = SAMPLE_FILES_DIR / 'subdirectory_001'
        self.filedict_filled_2['dir1_rel'] = './subdirectory_001'

    def test_nonexistent_base_dir(self):
        # Verifies that an error is thrown for a non-existent base directory
        with self.assertRaises(NotADirectoryError):
            FileDictionary(SAMPLE_FILES_DIR / 'nonexistent_dir')

    def test_get_base_dir(self):
        # Verifies that base directory is correctly retrieved
        self.assertEqual(self.filedict.base_dir, pathlib.Path(SAMPLE_FILES_DIR))

    def test_add_items(self):
        # Verifies that items can be added to the file dictionary
        self.assertDictEqual(self.filedict, {})

        self.filedict.add('file1', SAMPLE_FILES_DIR / 'general_text_file_001.txt')
        self.filedict.add('file2', 'general_text_file_002.txt')
        self.filedict.add('file3', 'nonexistent_file.ipynb')

        self.assertDictEqual(
            self.filedict,
            {
                'file1': SAMPLE_FILES_DIR / 'general_text_file_001.txt',
                'file2': pathlib.Path('general_text_file_002.txt'),
                'file3': pathlib.Path('nonexistent_file.ipynb'),
            }
        )

    def test_add_items_brackets(self):
        # Verifies that items can be added to the file dictionary with
        # bracket notation
        self.assertDictEqual(
            self.filedict_filled_1,
            {
                'file1': SAMPLE_FILES_DIR / 'general_text_file_001.txt',
                'file2': pathlib.Path('general_text_file_002.txt'),
                'file3': pathlib.Path('nonexistent_file.ipynb'),
            }
        )

    def test_add_batch(self):
        # Verifies that a batch of items can be added to the file dictionary
        self.assertDictEqual(self.filedict, {})

        self.filedict.add_batch(
            ['file1', 'file2', 'file3'],
            [
                SAMPLE_FILES_DIR / 'general_text_file_001.txt',
                'general_text_file_002.txt',
                'nonexistent_file.ipynb',
            ]
        )

        self.assertDictEqual(
            self.filedict,
            {
                'file1': SAMPLE_FILES_DIR / 'general_text_file_001.txt',
                'file2': pathlib.Path('general_text_file_002.txt'),
                'file3': pathlib.Path('nonexistent_file.ipynb'),
            }
        )

    def test_add_batch_incorrect_type(self):
        # Verifies that an error is thrown if attempting to add a batch
        # of items to the file dictionary with incorrect type
        self.assertDictEqual(self.filedict, {})

        with self.assertRaises(TypeError):
            self.filedict.add_batch(
                'invalid_type',
                [
                    SAMPLE_FILES_DIR / 'general_text_file_001.txt',
                    'general_text_file_002.txt',
                    'nonexistent_file.ipynb',
                ]
            )

        with self.assertRaises(TypeError):
            self.filedict.add_batch(
                ['file1', 'file2', 'file3'],
                {'invalid_type': True}
            )

    def test_add_batch_unequal_len(self):
        # Verifies that an error is thrown if attempting to add a batch
        # of items to the file dictionary with differing input lengths
        self.assertDictEqual(self.filedict, {})

        with self.assertRaises(ValueError):
            self.filedict.add_batch(
                ['file1', 'file2', 'file3'],
                ['general_text_file_001.txt', 'general_text_file_002.txt'])

    def test_add_overwrite(self):
        # Verifies that overwrite warnings are displayed as expected
        with self.assertRaises(FileDictionaryPathExistsError):
            self.filedict_filled_1.add('file1', 'new_path')

        self.filedict_filled_1.add('file1', 'new_path', overwrite=True)
        self.assertDictEqual(
            self.filedict_filled_1,
            {
                'file1': pathlib.Path('new_path'),
                'file2': pathlib.Path('general_text_file_002.txt'),
                'file3': pathlib.Path('nonexistent_file.ipynb'),
            }
        )

    def test_get_raw(self):
        # Verifies that paths are correctly retrieved from the dictionary
        self.assertEqual(
            self.filedict_filled_2.get_raw('file1_abs'),
            SAMPLE_FILES_DIR / 'general_text_file_001.txt')

        self.assertEqual(
            self.filedict_filled_2.get_raw('file1_rel'),
            pathlib.Path('general_text_file_001.txt'))

        self.assertEqual(
            self.filedict_filled_2.get_raw('file2_abs'),
            SAMPLE_FILES_DIR / 'subdirectory_001' / 'sample_subfile_001.txt')

        self.assertEqual(
            self.filedict_filled_2.get_raw('file2_rel'),
            pathlib.Path('subdirectory_001/sample_subfile_001.txt'))

        self.assertEqual(
            self.filedict_filled_2.get_raw('dir1_abs'),
            SAMPLE_FILES_DIR / 'subdirectory_001')

        self.assertEqual(
            self.filedict_filled_2.get_raw('dir1_rel'),
            pathlib.Path('subdirectory_001/'))

    def test_get_abs(self):
        # Verifies that absolute paths are correctly retrieved from
        # the dictionary
        self.assertEqual(
            self.filedict_filled_2.get_abs('file1_abs'),
            SAMPLE_FILES_DIR / 'general_text_file_001.txt')

        self.assertEqual(
            self.filedict_filled_2.get_abs('file1_rel'),
            SAMPLE_FILES_DIR / 'general_text_file_001.txt')

        self.assertEqual(
            self.filedict_filled_2.get_abs('file2_abs'),
            SAMPLE_FILES_DIR / 'subdirectory_001' / 'sample_subfile_001.txt')

        self.assertEqual(
            self.filedict_filled_2.get_abs('file2_rel'),
            SAMPLE_FILES_DIR / 'subdirectory_001' / 'sample_subfile_001.txt')

        self.assertEqual(
            self.filedict_filled_2.get_abs('dir1_abs'),
            SAMPLE_FILES_DIR / 'subdirectory_001')

        self.assertEqual(
            self.filedict_filled_2.get_abs('dir1_rel'),
            SAMPLE_FILES_DIR / 'subdirectory_001')

    def test_get_nonexistent(self):
        # Verifies that an error is thrown if attempting to retrieve a path
        # with a key that doesn't exist in the file dictionary
        with self.assertRaises(KeyError):
            self.filedict_filled_2.get_raw('invalid_key')

        with self.assertRaises(KeyError):
            self.filedict_filled_2.get_abs('invalid_key')

    def test_validate_paths_exist(self):
        # Verifies that paths in file dictionary are correctly identified
        # as existing when all exist
        with CapturePrint() as terminal_stdout:
            outputs = self.filedict_filled_2.validate_paths()
            text = terminal_stdout.getvalue()

        self.assertTupleEqual(outputs, (True, 6, 0))
        self.assertEqual(
            text,
            (f'Checked 6 path(s)\n'
             f'\n'
             f'The following 6 path(s) exist:\n'
             f'file1_abs :  {SAMPLE_FILES_DIR / "general_text_file_001.txt"}\n'
             f'file1_rel :  general_text_file_001.txt\n'
             f'file2_abs :  {SAMPLE_FILES_DIR / "subdirectory_001" / "sample_subfile_001.txt"}\n'
             f'file2_rel :  subdirectory_001/sample_subfile_001.txt\n'
             f'dir1_abs  :  {SAMPLE_FILES_DIR / "subdirectory_001"}\n'
             f'dir1_rel  :  subdirectory_001\n'
             f'\n'
             f'All path(s) in dictionary exist\n'
            )
        )

    def test_validate_paths_exist_noprint(self):
        # Verifies that paths in file dictionary are correctly identified
        # as existing when all exist with printing disabled
        self.assertTupleEqual(
            self.filedict_filled_2.validate_paths(False),
            (True, 6, 0))

    def test_validate_paths_nonexist(self):
        # Verifies that paths in file dictionary are correctly identified
        # as not all existing existing when some do not exist
        with CapturePrint() as terminal_stdout:
            outputs = self.filedict_filled_1.validate_paths()
            text = terminal_stdout.getvalue()

        self.assertTupleEqual(outputs, (False, 2, 1))
        self.assertEqual(
            text,
            (f'Checked 3 path(s)\n'
             f'\n'
             f'The following 2 path(s) exist:\n'
             f'file1 :  {SAMPLE_FILES_DIR / "general_text_file_001.txt"}\n'
             f'file2 :  general_text_file_002.txt\n'
             f'\n'
             f'The following 1 path(s) do NOT exist:\n'
             f'file3 :  nonexistent_file.ipynb\n'
            )
        )

    def test_validate_paths_nonexist_noprint(self):
        # Verifies that paths in file dictionary are correctly identified
        # as not all existing existing when some do not exist with
        # printing disabled
        self.assertTupleEqual(
            self.filedict_filled_1.validate_paths(False),
            (False, 2, 1))
