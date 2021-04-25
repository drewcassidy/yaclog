import unittest
import yaclog
import os.path
import datetime

test_dir = os.path.dirname(os.path.realpath(__file__))


class TestParser(unittest.TestCase):
    def setUp(self):
        self.log = yaclog.read(os.path.join(test_dir, 'Test-Changelog.md'))

    def test_header(self):
        self.assertEqual(self.log.header,
                         '# Changelog\n\n'
                         'This changelog is for testing the parser, and has many things in it that might trip it up.')

    def test_path(self):
        self.assertEqual(self.log.path, os.path.join(test_dir, 'Test-Changelog.md'))

    def test_links(self):
        self.assertEqual(self.log.links, {'unreleased': 'http://beesbeesbees.com',
                                          '1.1.0': 'http://endless.horse',
                                          'id': 'http://www.koalastothemax.com'})

    def test_versions(self):
        v = self.log.versions
        self.assertEqual(v[0].name, 'Unreleased')
        self.assertEqual(v[0].link, 'http://beesbeesbees.com')
        self.assertEqual(v[0].date, None)
        self.assertEqual(v[0].tags, [])

        self.assertEqual(v[1].name, '1.1.0')
        self.assertEqual(v[1].link, 'http://endless.horse')
        self.assertEqual(v[1].date, datetime.date.fromisoformat('1969-07-20'))
        self.assertEqual(v[1].tags, ['PRERELEASE'])

        self.assertEqual(v[2].name, 'Not a version number')
        self.assertEqual(v[2].link, None)
        self.assertEqual(v[2].date, None)
        self.assertEqual(v[2].tags, [])

    def test_unreleased(self):
        v = self.log.versions[0]

        self.assertEqual(v.sections[''], ['- bullet point with no section'])
        self.assertEqual(v.sections['Added'],
                         ['- bullet point dash', '* bullet point star',
                          '+ bullet point plus\n  - sub point 1\n  - sub point 2\n  - sub point 3'])
        self.assertEqual(v.sections['Fixed'],
                         ['- this is a bullet point\n  it spans many lines',
                          'This is\na paragraph\nit spans many lines',
                          'this line has an [id] link',
                          '#### This is an H4',
                          '##### This is an H5',
                          '###### This is an H6',
                          '```markdown\nthis is some example code\nit spans many lines\n```',
                          '> this is a block quote\nit spans many lines'])


if __name__ == '__main__':
    unittest.main()
