import datetime
import os.path
import tempfile
import unittest

import yaclog
from tests.common import log, log_segments, log_text
from yaclog.changelog import VersionEntry


class TestParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as td:
            cls.path = os.path.join(td, 'changelog.md')
            with open(cls.path, 'w') as fd:
                fd.write(log_text)
            cls.log = yaclog.read(cls.path)

    def test_path(self):
        """Test the log's path"""
        self.assertEqual(self.path, self.log.path)

    def test_preamble(self):
        """Test the preamble at the top of the file"""
        self.assertEqual(log.preamble, self.log.preamble)

    def test_links(self):
        """Test the links at the end of the file"""
        self.assertEqual({'fullversion': 'http://endless.horse', **log.links}, self.log.links)

    def test_versions(self):
        """Test the version headers"""
        for i in range(len(self.log.versions)):
            self.assertEqual(log.versions[i].name, self.log.versions[i].name)
            self.assertEqual(log.versions[i].link, self.log.versions[i].link)
            self.assertEqual(log.versions[i].date, self.log.versions[i].date)
            self.assertEqual(log.versions[i].tags, self.log.versions[i].tags)

    def test_entries(self):
        """Test the change entries"""
        self.assertEqual(log.versions[0].sections, self.log.versions[0].sections)


class TestWriter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as td:
            cls.path = os.path.join(td, 'changelog.md')
            log.write(cls.path)
            with open(cls.path) as fd:
                cls.log_text = fd.read()
                cls.log_segments = [line.lstrip('\n') for line in cls.log_text.split('\n\n') if line]

    def test_preamble(self):
        """Test the header information at the top of the file"""
        self.assertEqual(log_segments[0:2], self.log_segments[0:2])

    def test_links(self):
        """Test the links at the end of the file"""
        self.assertEqual(
            {'[fullversion]: http://endless.horse', '[id]: http://www.koalastothemax.com'},
            set(self.log_segments[16:18]))

    def test_versions(self):
        """Test the version headers"""
        self.assertEqual('## [Tests]', self.log_segments[2])
        self.assertEqual('## [FullVersion] - 1969-07-20 [TAG1] [TAG2]', self.log_segments[14])
        self.assertEqual('## Long Version Name', self.log_segments[15])

    def test_entries(self):
        """Test the change entries"""
        self.assertEqual(log_segments[3], self.log_segments[3])
        self.assertEqual('### Bullet Points', self.log_segments[4])
        self.assertEqual(log_segments[5], self.log_segments[5])
        self.assertEqual('### Blocks', self.log_segments[6])
        self.assertEqual(log_segments[7:14], self.log_segments[7:14])


class TestVersionEntry(unittest.TestCase):
    def test_header_name(self):
        """Test reading version names from headers"""
        headers = {
            'short': ('## Test', 'Test'),
            'with dash': ('## Test - ', 'Test'),
            'multi word': ('## Very long version name 1.0.0', 'Very long version name 1.0.0'),
            'with brackets': ('## [Test]', '[Test]'),
        }

        for c, t in headers.items():
            h = t[0]
            with self.subTest(c, h=h):
                version = VersionEntry.from_header(h)
                self.assertEqual(version.name, t[1])
                self.assertEqual(version.tags, [])
                self.assertIsNone(version.date)
                self.assertIsNone(version.link)
                self.assertIsNone(version.link_id)

    def test_header_tags(self):
        """Test reading version tags from headers"""
        headers = {
            'no dash': ('## Test [Foo] [Bar]', 'Test', ['FOO', 'BAR']),
            'with dash': ('## Test - [Foo] [Bar]', 'Test', ['FOO', 'BAR']),
            'with brackets': ('## [Test] [Foo] [Bar]', '[Test]', ['FOO', 'BAR']),
            'with brackets & dash': ('## [Test] - [Foo] [Bar]', '[Test]', ['FOO', 'BAR']),
        }

        for c, t in headers.items():
            h = t[0]
            with self.subTest(c, h=h):
                version = VersionEntry.from_header(h)
                self.assertEqual(version.name, t[1])
                self.assertEqual(version.tags, t[2])
                self.assertIsNone(version.date)
                self.assertIsNone(version.link)
                self.assertIsNone(version.link_id)

    def test_header_date(self):
        """Test reading version dates from headers"""

        headers = {
            'no dash': ('## Test 1961-04-12', 'Test',
                        datetime.date.fromisoformat('1961-04-12'), []),
            'with dash': ('## Test 1969-07-20', 'Test',
                          datetime.date.fromisoformat('1969-07-20'), []),
            'two dates': ('## 1981-07-20 1988-11-15', '1981-07-20',
                          datetime.date.fromisoformat('1988-11-15'), []),
            'single date': ('## 2020-05-30', '2020-05-30', None, []),
            'with tags': ('## 1.0.0 - 2021-04-19 [Foo] [Bar]', '1.0.0',
                          datetime.date.fromisoformat('2021-04-19'), ['FOO', 'BAR']),
        }

        for c, t in headers.items():
            h = t[0]
            with self.subTest(c, h=h):
                version = VersionEntry.from_header(h)
                self.assertEqual(version.name, t[1])
                self.assertEqual(version.date, t[2])
                self.assertEqual(version.tags, t[3])
                self.assertIsNone(version.link)
                self.assertIsNone(version.link_id)

    def test_header_noncompliant(self):
        """Test reading version that dont fit the schema, and should just be read as literals"""

        headers = {
            'no space between tags': 'Test [Foo][Bar]',
            'text at end': 'Test [Foo] [Bar] Test',
            'invalid date': 'Test - 9999-99-99',
        }

        for c, h in headers.items():
            with self.subTest(c, h=h):
                version = VersionEntry.from_header('## ' + h)
                self.assertEqual(version.name, h)
                self.assertEqual(version.tags, [])
                self.assertIsNone(version.date)
                self.assertIsNone(version.link)
                self.assertIsNone(version.link_id)


if __name__ == '__main__':
    unittest.main()
