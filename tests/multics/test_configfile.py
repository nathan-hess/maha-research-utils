import unittest

from mahautils.multics import MahaMulticsConfigFile
from mahautils.multics.exceptions import MahaMulticsFileFormatError


class Test_ConfigFile_ExtractSection(unittest.TestCase):
    def setUp(self):
        self.begin_regex = r'\s*begin_Section\s*{\s*'
        self.end_regex = r'\s*}\s*'
        self.section_line_regex = r'\s*([@?])\s*([\w\d\._]+)\s+\[([^\s]+)\]\s*'

        self.configfile01 = MahaMulticsConfigFile()
        self.configfile01.set_contents(
            ['# comment',
             '[config file]',
             'begin_Section{',
             '  @velocity [m/s]',
             '  ?acceleration    [m/s^2]',
             '}',
             '',
             '[data]',
            ],
            trailing_newline=True
        )

        self.configfile02 = MahaMulticsConfigFile()
        self.configfile02.set_contents(
            ['# comment',
             '[config file]',
             'begin_Section{',
             '  # Comment 1',
             '  @velocity [m/s]',
             ' #Comment2',
             '# comment3 ',
             '  ?acceleration    [m/s^2]',
             '   #  comment4',
             '}',
             'data = 42',
             '# comment',
             '# comment',
             'begin_Section{',
             '  ?pressure	[N/m/mm]',
             '  ?time    [hr]',
             ' #comment 5',
             '}',
             '',
             '[data]',
            ],
            trailing_newline=True
        )

        self.configfile03 = MahaMulticsConfigFile()
        self.configfile03.set_contents(
            ['# comment',
             '[config file]',
             'begin_Section{ @velocity [m/s]',
             '  ?acceleration    [m/s^2]',
             '}',
             '',
             '[data]',
            ],
            trailing_newline=True
        )

        self.configfile04 = MahaMulticsConfigFile()
        self.configfile04.set_contents(
            ['# comment',
             'begin_Section{',
             '  velocity [m/s]',
             '  ?acceleration    [m/s^2]',
             '[data]',
            ],
            trailing_newline=True
        )

    def test_extract_section_single(self):
        # Verifies that section can be extracted from a file with only a
        # single section
        section_groups, comments, next_line, num_sections \
            = self.configfile01.extract_section_by_keyword(
                section_label       = 'mySection',
                begin_regex        = self.begin_regex,
                end_regex          = self.end_regex,
                section_line_regex = self.section_line_regex
            )

        with self.subTest(quantity='groups'):
            self.assertListEqual(
                [x.groups() for x in section_groups],
                [('@', 'velocity', 'm/s'),
                 ('?', 'acceleration', 'm/s^2'),]
            )

        with self.subTest(quantity='comments'):
            self.assertListEqual(
                comments,
                [(), ()]
            )

        with self.subTest(quantity='next_line'):
            self.assertEqual(next_line, 8)

        with self.subTest(quantity='num_sections'):
            self.assertEqual(num_sections, 1)

    def test_extract_section_multiple_merge(self):
        # Verifies that all sections can be extracted from a file with
        # multiple sections
        section_groups, comments, next_line, num_sections \
            = self.configfile02.extract_section_by_keyword(
                section_label       = 'mySection',
                begin_regex        = self.begin_regex,
                end_regex          = self.end_regex,
                section_line_regex = self.section_line_regex
            )

        with self.subTest(quantity='groups'):
            self.assertListEqual(
                [x.groups() for x in section_groups],
                [('@', 'velocity', 'm/s'),
                 ('?', 'acceleration', 'm/s^2'),
                 ('?', 'pressure', 'N/m/mm'),
                 ('?', 'time', 'hr'),]
            )

        with self.subTest(quantity='comments'):
            self.assertListEqual(
                comments,
                [('  # Comment 1',),
                 (' #Comment2', '# comment3 '),
                 (),
                 (),]
            )

        with self.subTest(quantity='next_line'):
            self.assertEqual(next_line, 20)

        with self.subTest(quantity='num_sections'):
            self.assertEqual(num_sections, 2)

    def test_extract_section_multiple_restrict(self):
        # Verifies that one section can be extracted from a file with
        # multiple sections
        with self.subTest(section=1):
            section_groups, comments, next_line, num_sections \
                = self.configfile02.extract_section_by_keyword(
                    section_label       = 'mySection',
                    begin_regex        = self.begin_regex,
                    end_regex          = self.end_regex,
                    section_line_regex = self.section_line_regex,
                    max_sections       = 1,
                    begin_idx          = 0
                )

            with self.subTest(quantity='groups'):
                self.assertListEqual(
                    [x.groups() for x in section_groups],
                    [('@', 'velocity', 'm/s'),
                     ('?', 'acceleration', 'm/s^2'),]
                )

            with self.subTest(quantity='comments'):
                self.assertListEqual(
                    comments,
                    [('  # Comment 1',),
                     (' #Comment2', '# comment3 '),]
                )

            with self.subTest(quantity='next_line'):
                self.assertEqual(next_line, 10)

            with self.subTest(quantity='num_sections'):
                self.assertEqual(num_sections, 1)

        with self.subTest(section=2):
            section_groups, comments, next_line, num_sections \
                = self.configfile02.extract_section_by_keyword(
                    section_label       = 'mySection',
                    begin_regex        = self.begin_regex,
                    end_regex          = self.end_regex,
                    section_line_regex = self.section_line_regex,
                    max_sections       = 1,
                    begin_idx          = 11
                )

            with self.subTest(quantity='groups'):
                self.assertListEqual(
                    [x.groups() for x in section_groups],
                    [('?', 'pressure', 'N/m/mm'),
                     ('?', 'time', 'hr'),]
                )

            with self.subTest(quantity='comments'):
                self.assertListEqual(
                    comments,
                    [(), ()]
                )

            with self.subTest(quantity='next_line'):
                self.assertEqual(next_line, 18)

            with self.subTest(quantity='num_sections'):
                self.assertEqual(num_sections, 1)

    def test_no_section_line_regex(self):
        # Verifies that entire line is extracted if no section line
        # regex is specified
        section_groups = self.configfile01.extract_section_by_keyword(
            section_label       = 'mySection',
            begin_regex        = self.begin_regex,
            end_regex          = self.end_regex
        )[0]

        self.assertListEqual(
            [x.groups() for x in section_groups],
            [('  @velocity [m/s]',),
             ('  ?acceleration    [m/s^2]',),]
        )

    def test_data_same_line_header(self):
        # Verifies that section can be extracted from a file with only a
        # single section, the first line of data in the section is on the
        # same line as the section beginning identifier
        section_groups, comments, next_line, num_sections \
            = self.configfile03.extract_section_by_keyword(
                section_label       = 'mySection',
                begin_regex        = self.begin_regex,
                end_regex          = self.end_regex,
                section_line_regex = self.section_line_regex
            )

        with self.subTest(quantity='groups'):
            self.assertListEqual(
                [x.groups() for x in section_groups],
                [('@', 'velocity', 'm/s'),
                 ('?', 'acceleration', 'm/s^2'),]
            )

        with self.subTest(quantity='next_line'):
            self.assertEqual(next_line, 7)

        with self.subTest(quantity='num_sections'):
            self.assertEqual(num_sections, 1)

    def test_invalid_max_sections(self):
        # Verifies that an error is thrown if providing an invalid
        # maximum number of sections
        with self.assertRaises(ValueError):
            self.configfile01.extract_section_by_keyword(
                section_label       = 'mySection',
                begin_regex        = self.begin_regex,
                end_regex          = self.end_regex,
                section_line_regex = self.section_line_regex,
                max_sections       = -5
            )

    def test_no_section_end(self):
        # Verifies that an error is thrown if no end of section is found
        with self.assertRaises(MahaMulticsFileFormatError):
            self.configfile04.extract_section_by_keyword(
                section_label       = 'mySection',
                begin_regex        = self.begin_regex,
                end_regex          = self.end_regex
            )

    def test_no_regex_match(self):
        # Verifies that an error is thrown if section lines don't match regex
        with self.assertRaises(MahaMulticsFileFormatError):
            self.configfile04.extract_section_by_keyword(
                section_label       = 'mySection',
                begin_regex        = self.begin_regex,
                end_regex          = self.end_regex,
                section_line_regex = self.section_line_regex
            )
