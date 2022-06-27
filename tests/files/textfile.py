import unittest

from mahautils.files import TextFile
from tests import SAMPLE_FILES_DIR


class Test_TextFile_SingleComment(unittest.TestCase):
    def setUp(self):
        # Read sample file
        self.file = TextFile(SAMPLE_FILES_DIR / 'general_text_file_002.txt',
                             comment_chars='#')
        self.file.read()

    def test_check_trailing_newline(self):
        # Verify that `TextFile.trailing_newline` correctly identifies
        # whether the file has a newline at the end of the file
        self.assertTrue(self.file.trailing_newline)

    def test_clean_removeComments(self):
        # Verify that `TextFile._clean_contents()` correctly
        # removes line comments
        self.file._clean_contents(
            remove_comments=True,
            skip_full_line_comments=False,
            strip=False,
            concat_lines=False,
            remove_blank_lines=False
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '', ' Li', 'Ln ', '', 'L5\\', 'Line6', 'Line7\\',
             'Li//ne8\\', 'line 9', '//lIne 10']
        )

    def test_clean_removeComments_skipFull(self):
        # Verify that `TextFile._clean_contents()` correctly removes line
        # comments, skipping full-line comments
        self.file._clean_contents(
            remove_comments=True,
            skip_full_line_comments=True,
            strip=False,
            concat_lines=False,
            remove_blank_lines=False
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '#Li//ne2\t  ', ' Li', 'Ln ', '', 'L5\\', 'Line6',
             'Line7\\', 'Li//ne8\\', 'line 9', '//lIne 10']
        )

    def test_clean_removeCommentsBlank(self):
        # Verify that `TextFile._clean_contents()` correctly removes line
        # comments and blank lines
        self.file._clean_contents(
            remove_comments=True,
            skip_full_line_comments=False,
            strip=False,
            concat_lines=False,
            remove_blank_lines=True
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', ' Li', 'Ln ', 'L5\\', 'Line6', 'Line7\\',
             'Li//ne8\\', 'line 9', '//lIne 10']
        )

    def test_clean_removeCommentsBlank_skipFull(self):
        # Verify that `TextFile._clean_contents()` correctly removes line
        # comments and blank lines, skipping full-line comments
        self.file._clean_contents(
            remove_comments=True,
            skip_full_line_comments=True,
            strip=False,
            concat_lines=False,
            remove_blank_lines=True
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '#Li//ne2\t  ', ' Li', 'Ln ', 'L5\\', 'Line6',
             'Line7\\', 'Li//ne8\\', 'line 9', '//lIne 10']
        )

    def test_clean_strip(self):
        # Verify that `TextFile._clean_contents()` correctly
        # strips whitespace from the beginning and end of lines
        self.file._clean_contents(
            remove_comments=False,
            skip_full_line_comments=False,
            strip=True,
            concat_lines=False,
            remove_blank_lines=False
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1', '#Li//ne2', 'Li#ne\\3', 'Ln #4', '', 'L5\\', 'Line6',
             'Line7\\', 'Li//ne8\\', 'line 9', '//lIne 10']
        )

    def test_clean_concat(self):
        # Verify that `TextFile._clean_contents()` correctly
        # concatenates lines ending with backslashes
        self.file._clean_contents(
            remove_comments=False,
            skip_full_line_comments=False,
            strip=False,
            concat_lines=True,
            remove_blank_lines=False
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '#Li//ne2\t  ', ' Li#ne\\3', 'Ln #4', '',
             'L5Line6', 'Line7Li//ne8line 9', '//lIne 10']
        )

    def test_clean_removeBlank(self):
        # Verify that `TextFile._clean_contents()` correctly
        # removes lines containing only whitespace
        self.file._clean_contents(
            remove_comments=False,
            skip_full_line_comments=False,
            strip=False,
            concat_lines=False,
            remove_blank_lines=True
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '#Li//ne2\t  ', ' Li#ne\\3', 'Ln #4', 'L5\\',
             'Line6', 'Line7\\', 'Li//ne8\\', 'line 9', '//lIne 10']
        )

    def test_concat_removeComments_skipFull(self):
        # Verify that `TextFile._clean_contents()` correctly concatenates
        # lines ending with backslashes and removes comments, skipping
        # full-line comments
        self.file._clean_contents(
            remove_comments=True,
            skip_full_line_comments=True,
            strip=False,
            concat_lines=True,
            remove_blank_lines=False
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '#Li//ne2\t  ', ' Li', 'Ln ', '',
             'L5Line6', 'Line7Li//ne8line 9', '//lIne 10']
        )

    def test_concat_removeComments(self):
        # Verify that `TextFile._clean_contents()` correctly concatenates
        # lines ending with backslashes and removes comments
        self.file._clean_contents(
            remove_comments=True,
            skip_full_line_comments=False,
            strip=False,
            concat_lines=True,
            remove_blank_lines=False
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '', ' Li', 'Ln ', '', 'L5Line6',
             'Line7Li//ne8line 9', '//lIne 10']
        )


class Test_TextFile_NoTrailingNewline(unittest.TestCase):
    def setUp(self):
        # Read sample file
        self.file = TextFile(SAMPLE_FILES_DIR / 'general_text_file_003.txt',
                             comment_chars='#')
        self.file.read()

    def test_check_trailing_newline(self):
        # Verify that `TextFile.trailing_newline` correctly identifies
        # whether the file has a newline at the end of the file
        self.assertFalse(self.file.trailing_newline)


class Test_TextFile_MultiComment(unittest.TestCase):
    def setUp(self):
        # Read sample file
        self.file = TextFile(SAMPLE_FILES_DIR / 'general_text_file_002.txt',
                             comment_chars=('//', '#'))
        self.file.read()

    def test_check_trailing_newline(self):
        # Verify that `TextFile.trailing_newline` correctly identifies
        # whether the file has a newline at the end of the file
        self.assertTrue(self.file.trailing_newline)

    def test_clean_removeComments(self):
        # Verify that `TextFile._clean_contents()` correctly
        # removes line comments
        self.file._clean_contents(
            remove_comments=True,
            skip_full_line_comments=False,
            strip=False,
            concat_lines=False,
            remove_blank_lines=False
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '', ' Li', 'Ln ', '', 'L5\\', 'Line6', 'Line7\\',
             'Li', 'line 9', '']
        )

    def test_clean_removeComments_skipFull(self):
        # Verify that `TextFile._clean_contents()` correctly removes line
        # comments, skipping full-line comments
        self.file._clean_contents(
            remove_comments=True,
            skip_full_line_comments=True,
            strip=False,
            concat_lines=False,
            remove_blank_lines=False
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '#Li//ne2\t  ', ' Li', 'Ln ', '', 'L5\\', 'Line6',
             'Line7\\', 'Li', 'line 9', '//lIne 10']
        )

    def test_clean_removeCommentsBlank(self):
        # Verify that `TextFile._clean_contents()` correctly removes line
        # comments and blank lines
        self.file._clean_contents(
            remove_comments=True,
            skip_full_line_comments=False,
            strip=False,
            concat_lines=False,
            remove_blank_lines=True
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', ' Li', 'Ln ', 'L5\\', 'Line6', 'Line7\\',
             'Li', 'line 9']
        )

    def test_clean_removeCommentsBlank_skipFull(self):
        # Verify that `TextFile._clean_contents()` correctly removes line
        # comments and blank lines, skipping full-line comments
        self.file._clean_contents(
            remove_comments=True,
            skip_full_line_comments=True,
            strip=False,
            concat_lines=False,
            remove_blank_lines=True
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '#Li//ne2\t  ', ' Li', 'Ln ', 'L5\\', 'Line6',
             'Line7\\', 'Li', 'line 9', '//lIne 10']
        )

    def test_clean_strip(self):
        # Verify that `TextFile._clean_contents()` correctly
        # strips whitespace from the beginning and end of lines
        self.file._clean_contents(
            remove_comments=False,
            skip_full_line_comments=False,
            strip=True,
            concat_lines=False,
            remove_blank_lines=False
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1', '#Li//ne2', 'Li#ne\\3', 'Ln #4', '', 'L5\\',
             'Line6', 'Line7\\', 'Li//ne8\\', 'line 9', '//lIne 10']
        )

    def test_clean_concat(self):
        # Verify that `TextFile._clean_contents()` correctly
        # concatenates lines ending with backslashes
        self.file._clean_contents(
            remove_comments=False,
            skip_full_line_comments=False,
            strip=False,
            concat_lines=True,
            remove_blank_lines=False
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '#Li//ne2\t  ', ' Li#ne\\3', 'Ln #4', '',
             'L5Line6', 'Line7Li//ne8line 9', '//lIne 10']
        )

    def test_clean_removeBlank(self):
        # Verify that `TextFile._clean_contents()` correctly
        # removes lines containing only whitespace
        self.file._clean_contents(
            remove_comments=False,
            skip_full_line_comments=False,
            strip=False,
            concat_lines=False,
            remove_blank_lines=True
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '#Li//ne2\t  ', ' Li#ne\\3', 'Ln #4', 'L5\\',
             'Line6', 'Line7\\', 'Li//ne8\\', 'line 9', '//lIne 10']
        )

    def test_concat_removeComments_skipFull(self):
        # Verify that `TextFile._clean_contents()` correctly concatenates
        # lines ending with backslashes and removes comments, skipping
        # full-line comments
        self.file._clean_contents(
            remove_comments=True,
            skip_full_line_comments=True,
            strip=False,
            concat_lines=True,
            remove_blank_lines=False
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '#Li//ne2\t  ', ' Li', 'Ln ', '',
             'L5Line6', 'Line7Li', '//lIne 10']
        )

    def test_concat_removeComments(self):
        # Verify that `TextFile._clean_contents()` correctly concatenates
        # lines ending with backslashes and removes comments
        self.file._clean_contents(
            remove_comments=True,
            skip_full_line_comments=False,
            strip=False,
            concat_lines=True,
            remove_blank_lines=False
        )

        self.assertListEqual(
            self.file.contents,
            ['Line1 ', '', ' Li', 'Ln ', '', 'L5Line6', 'Line7Li', '']
        )
