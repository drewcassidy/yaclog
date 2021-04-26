import os.path
import tempfile
import unittest

import yaclog.changelog
from tests.common import log, log_segments, log_text


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

    def test_header(self):
        """Test the header information at the top of the file"""
        self.assertEqual(log.header, self.log.header)

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
                cls.log_segments = [line for line in cls.log_text.split('\n\n') if line]

    def test_header(self):
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


if __name__ == '__main__':
    unittest.main()
