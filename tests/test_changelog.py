import unittest
import yaclog.changelog
import os.path
import datetime
import textwrap
import tempfile
from tests.common import log, log_segments, log_text


class TestParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as td:
            cls.path = os.path.join(td, 'changelog.md')
            with open(cls.path, 'w') as fd:
                fd.write(log_text)
            cls.log = yaclog.read(cls.path)

    def test_header(self):
        self.assertEqual(log.header, self.log.header)

    def test_path(self):
        self.assertEqual(self.path, self.log.path)

    def test_links(self):
        self.assertEqual({'fullversion': 'http://endless.horse', **log.links}, self.log.links)

    def test_versions(self):
        for i in range(len(self.log.versions)):
            self.assertEqual(log.versions[i].name, self.log.versions[i].name)
            self.assertEqual(log.versions[i].link, self.log.versions[i].link)
            self.assertEqual(log.versions[i].date, self.log.versions[i].date)
            self.assertEqual(log.versions[i].tags, self.log.versions[i].tags)

    def test_Entries(self):
        self.assertEqual(log.versions[0].sections, self.log.versions[0].sections)


if __name__ == '__main__':
    unittest.main()
