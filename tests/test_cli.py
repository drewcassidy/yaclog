import unittest
import os.path
import git

import yaclog
from yaclog.cli.__main__ import cli
from click.testing import CliRunner


class TestCreation(unittest.TestCase):
    def test_init(self):
        """Test creating and overwriting a changelog"""
        runner = CliRunner()
        location = 'CHANGELOG.md'
        err_str = 'THIS FILE WILL BE OVERWRITTEN'

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['init'])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue(os.path.exists(os.path.abspath(location)), 'yaclog init did not create a file')
            self.assertIn(location, result.output, "yaclog init did not echo the file's correct location")

            with open(location, 'w') as fp:
                fp.write(err_str)

            result = runner.invoke(cli, ['init'], input='y\n')
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue(os.path.exists(os.path.abspath(location)), 'file no longer exists after overwrite')
            self.assertIn(location, result.output, "yaclog init did not echo the file's correct location")

            with open(location, 'r') as fp:
                self.assertNotEqual(fp.read(), err_str, 'file was not overwritten')

    def test_init_path(self):
        """Test creating a changelog with a non-default filename"""
        runner = CliRunner()
        location = 'A different file.md'

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['--path', location, 'init'])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue(os.path.exists(os.path.abspath(location)), 'yaclog init did not create a file')
            self.assertIn(location, result.output, "yaclog init did not echo the file's correct location")

    def test_does_not_exist(self):
        """Test if an error is thrown when the file does not exist"""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['show'])
            self.assertNotEqual(result.exit_code, 0, result.output)
            self.assertIn('does not exist', result.output)


class TestTagging(unittest.TestCase):
    def test_tag_addition(self):
        runner = CliRunner()
        location = 'CHANGELOG.md'

        with runner.isolated_filesystem():
            in_log = yaclog.Changelog(location)
            in_log.versions = [yaclog.changelog.VersionEntry(), yaclog.changelog.VersionEntry()]

            in_log.versions[0].name = '1.0.0'
            in_log.versions[1].name = '0.9.0'
            in_log.write()

            result = runner.invoke(cli, ['tag', 'tag1'])
            self.assertEqual(result.exit_code, 0, result.output)

            result = runner.invoke(cli, ['tag', 'tag2', '0.9.0'])
            self.assertEqual(result.exit_code, 0, result.output)

            out_log = yaclog.read(location)
            self.assertEqual(out_log.versions[0].tags, ['TAG1'])
            self.assertEqual(out_log.versions[1].tags, ['TAG2'])

            result = runner.invoke(cli, ['tag', 'tag3', '0.8.0'])
            self.assertNotEqual(result.exit_code, 0, result.output)
            self.assertIn('not found in changelog', result.output)

    def test_tag_deletion(self):
        runner = CliRunner()
        location = 'CHANGELOG.md'

        with runner.isolated_filesystem():
            in_log = yaclog.Changelog(location)
            in_log.versions = [None, None]
            in_log.versions = [yaclog.changelog.VersionEntry(), yaclog.changelog.VersionEntry()]

            in_log.versions[0].name = '1.0.0'
            in_log.versions[0].tags = ['TAG1']

            in_log.versions[1].name = '0.9.0'
            in_log.versions[1].tags = ['TAG2']
            in_log.write()

            result = runner.invoke(cli, ['tag', '-d', 'tag2', '0.8.0'])
            self.assertNotEqual(result.exit_code, 0, result.output)
            self.assertIn('not found in changelog', result.output)

            result = runner.invoke(cli, ['tag', '-d', 'tag3', '0.9.0'])
            self.assertNotEqual(result.exit_code, 0, result.output)
            self.assertIn('not found in version', result.output)

            result = runner.invoke(cli, ['tag', '-d', 'tag1'])
            self.assertNotIn('not found in version', result.output)
            self.assertEqual(result.exit_code, 0, result.output)

            out_log = yaclog.read(location)
            self.assertEqual(out_log.versions[0].tags, [])
            self.assertEqual(out_log.versions[1].tags, ['TAG2'])

            result = runner.invoke(cli, ['tag', '-d', 'tag2', '0.9.0'])
            self.assertNotIn('not found in version', result.output)
            self.assertEqual(result.exit_code, 0, result.output)

            out_log = yaclog.read(location)
            self.assertEqual(out_log.versions[0].tags, [])
            self.assertEqual(out_log.versions[1].tags, [])


class TestRelease(unittest.TestCase):
    def test_increment(self):
        runner = CliRunner()
        location = 'CHANGELOG.md'

        with runner.isolated_filesystem():
            runner.invoke(cli, ['init'])  # create the changelog
            runner.invoke(cli, ['entry', '-b', 'entry number 1'])

            result = runner.invoke(cli, ['release', '--version', '1.0.0'])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(yaclog.read(location).versions[0].name, '1.0.0')
            self.assertIn('Unreleased', result.output)
            self.assertIn('1.0.0', result.output)

            runner.invoke(cli, ['entry', '-b', 'entry number 2'])

            result = runner.invoke(cli, ['release', '-p'])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(yaclog.read(location).versions[0].name, '1.0.1')
            self.assertIn('Unreleased', result.output)
            self.assertIn('1.0.1', result.output)

            runner.invoke(cli, ['entry', '-b', 'entry number 3'])

            result = runner.invoke(cli, ['release', '-m'])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(yaclog.read(location).versions[0].name, '1.1.0')
            self.assertIn('Unreleased', result.output)
            self.assertIn('1.1.0', result.output)

            runner.invoke(cli, ['entry', '-b', 'entry number 4'])

            result = runner.invoke(cli, ['release', '-M'])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(yaclog.read(location).versions[0].name, '2.0.0')
            self.assertIn('Unreleased', result.output)
            self.assertIn('2.0.0', result.output)

    def test_commit(self):
        runner = CliRunner()

        with runner.isolated_filesystem():
            repo = git.Repo.init(os.path.join(os.curdir, 'testing'))
            os.chdir('testing')
            repo.index.commit('initial commit')

            runner.invoke(cli, ['init'])  # create the changelog
            runner.invoke(cli, ['entry', '-b', 'entry number 1'])

            result = runner.invoke(cli, ['release', '--version', '1.0.0', '-c'], input='y\n')
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn('Created commit', result.output)
            self.assertIn('Created tag', result.output)
            self.assertIn(repo.head.commit.hexsha[0:7], result.output)
            self.assertEqual(repo.tags[0].name, '1.0.0')


if __name__ == '__main__':
    unittest.main()
