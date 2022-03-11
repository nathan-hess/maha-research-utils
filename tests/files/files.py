##############################################################################
# --- IMPORT DEPENDENCIES -------------------------------------------------- #
##############################################################################
# Standard library imports
import unittest

# Custom package and module imports
import multics


##############################################################################
# --- TEST CASES: GENERAL FILES CLASS -------------------------------------- #
##############################################################################
class Test_Files(unittest.TestCase):
    def test_clean_removeComments(self):
        # Verify that `multics.files.File.clean_contents()` correctly
        # removes line comments
        file = multics.files.File(comment_char='#')
        file.set_contents(['Line1 ', '#Line2\t  ', ' Li#ne\\3', 'Ln #4', '\n',
                           'L5\\', 'Line6', 'Line7\\', 'Line8\\', 'line 9'])

        file.clean_contents(
            remove_comments=True,
            strip=False,
            concat_lines=False,
            remove_blank_lines=False
        )

        self.assertEqual(
            file.contents,
            ['Line1 ', ' Li', 'Ln ', '\n', 'L5\\', 'Line6', 'Line7\\',
             'Line8\\', 'line 9']
        )
    
    def test_clean_strip(self):
        # Verify that `multics.files.File.clean_contents()` correctly
        # strips whitespace from the beginning and end of lines
        file = multics.files.File(comment_char='#')
        file.set_contents(['Line1 ', '#Line2\t  ', ' Li#ne\\3', 'Ln #4', '\n',
                           'L5\\', 'Line6', 'Line7\\', 'Line8\\', 'line 9'])

        file.clean_contents(
            remove_comments=False,
            strip=True,
            concat_lines=False,
            remove_blank_lines=False
        )

        self.assertEqual(
            file.contents,
            ['Line1', '#Line2', 'Li#ne\\3', 'Ln #4', '',
             'L5\\', 'Line6', 'Line7\\', 'Line8\\', 'line 9']
        )
    
    def test_clean_concat(self):
        # Verify that `multics.files.File.clean_contents()` correctly
        # concatenates lines ending with backslashes
        file = multics.files.File(comment_char='#')
        file.set_contents(['Line1 ', '#Line2\t  ', ' Li#ne\\3', 'Ln #4', '\n',
                           'L5\\', 'Line6', 'Line7\\', 'Line8\\', 'line 9'])

        file.clean_contents(
            remove_comments=False,
            strip=False,
            concat_lines=True,
            remove_blank_lines=False
        )

        self.assertEqual(
            file.contents,
            ['Line1 ', '#Line2\t  ', ' Li#ne\\3', 'Ln #4', '\n',
             'L5Line6', 'Line7Line8line 9']
        )

    def test_clean_removeBlank(self):
        # Verify that `multics.files.File.clean_contents()` correctly
        # removes lines containing only whitespace
        file = multics.files.File(comment_char='#')
        file.set_contents(['Line1 ', '#Line2\t  ', ' Li#ne\\3', 'Ln #4', '\n',
                           'L5\\', 'Line6', 'Line7\\', 'Line8\\', 'line 9'])

        file.clean_contents(
            remove_comments=False,
            strip=False,
            concat_lines=False,
            remove_blank_lines=True
        )

        self.assertEqual(
            file.contents,
            ['Line1 ', '#Line2\t  ', ' Li#ne\\3', 'Ln #4',
             'L5\\', 'Line6', 'Line7\\', 'Line8\\', 'line 9']
        )
