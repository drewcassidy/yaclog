#  yaclog: yet another changelog tool
#  Copyright (c) 2021. Andrew Cassidy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import os.path
from sys import stdout

import click

import yaclog.version
from yaclog.changelog import Changelog


@click.group()
@click.option('--path', envvar='YACLOG_PATH', metavar='FILE', default='CHANGELOG.md', show_default=True,
              type=click.Path(dir_okay=False, writable=True, readable=True),
              help='Location of the changelog file.')
@click.version_option()
@click.pass_context
def cli(ctx, path):
    """Manipulate markdown changelog files."""
    if not (ctx.invoked_subcommand == 'init') and not os.path.exists(path):
        # file does not exist and this isn't the init command
        raise click.FileError(f'Changelog file {path} does not exist. Create it by running yaclog init.')

    ctx.obj = yaclog.read(path)


@cli.command()
@click.pass_obj
def init(obj: Changelog):
    """Create a new changelog file."""
    if os.path.exists(obj.path):
        click.confirm(f'Changelog file {obj.path} already exists. Would you like to overwrite it?', abort=True)
        os.remove(obj.path)

    yaclog.Changelog(obj.path).write()
    click.echo(f'Created new changelog file at {obj.path}')


@cli.command('format')  # don't accidentally hide the `format` python builtin
@click.pass_obj
def reformat(obj: Changelog):
    """Reformat the changelog file."""
    obj.write()
    click.echo(f'Reformatted changelog file at {obj.path}')


# noinspection PyShadowingNames
@cli.command(short_help='Show changes from the changelog file')
@click.option('--all', '-a', 'all_versions', is_flag=True, help='Show the entire changelog.')
@click.option('--markdown/--txt', '-m/-t', default=False, help='Display as markdown or plain text.')
@click.option('--full', '-f', 'mode', flag_value='full', default=True,
              help='Show version header and body.')
@click.option('--name', '-n', 'mode', flag_value='name',
              help='Show only the version name')
@click.option('--body', '-b', 'mode', flag_value='body',
              help='Show only the version body.')
@click.option('--header', '-h', 'mode', flag_value='header',
              help='Show only the version header.')
@click.option('--version', '-v', 'mode', flag_value='version', help='Show only the version number. If the current version is unreleased, '
                                                                    'this is inferred by incrementing the patch number of the last released version')
@click.option('---gh-actions', 'gh_actions', is_flag=True, hidden=True)
@click.argument('version_names', metavar='VERSIONS', type=str, nargs=-1)
@click.pass_obj
def show(obj: Changelog, all_versions, markdown, mode, version_names, gh_actions):
    """
    Show the changes for VERSIONS.

    VERSIONS is a list of versions to print. If not given, the most recent version is used.
    """

    functions = {
        'full': (lambda v, k: v.text(**k)),
        'name': (lambda v, k: v.name),
        'body': (lambda v, k: v.body(**k)),
        'header': (lambda v, k: v.header(**k)),
        'version': (lambda v, k: latest_version)
    }

    str_func = functions[mode]
    kwargs = {'md': markdown, 'color': stdout.isatty()}
    latest_version = str(obj.versions[0].version)

    try:
        if all_versions:
            versions = obj.versions
        elif len(version_names) == 0:
            versions = [obj.current_version()]
            if ((mode == 'version') or gh_actions) and versions[0].name == 'Unreleased':
                latest = obj.current_version(released=True).version
                inferred = yaclog.version.increment_version(str(latest), 2, '')
                latest_version = inferred
        else:
            versions = [obj.get_version(name) for name in version_names]
    except KeyError as k:
        raise click.BadArgumentUsage(str(k))
    except ValueError as v:
        raise click.ClickException(str(v))

    sep = '\n\n' if mode == 'body' or mode == 'full' else '\n'

    if gh_actions:
        import tempfile

        kwargs['color'] = False
        all_modes = [ 'name', 'header', 'version' ]
        outputs = [f'{mode}={sep.join([functions[mode](v, kwargs) for v in versions])}' for mode in all_modes]
        click.echo('\n'.join(outputs))
        body_fd, body_file = tempfile.mkstemp(text=True)
        with os.fdopen(body_fd, 'w') as f:
            f.write(sep.join([functions['body'](v, kwargs) for v in versions]))
        click.echo(f'body-file={body_file}')
        click.echo(f'changelog={obj.path}')
        return

    click.echo(sep.join([str_func(v, kwargs) for v in versions]))


@cli.command(short_help='Modify version tags')
@click.option('--add/--delete', '-a/-d', default=True, is_flag=True, help='Add or delete tags')
@click.argument('tag_name', metavar='TAG', type=str)
@click.argument('version_name', metavar='VERSION', type=str, required=False)
@click.pass_obj
def tag(obj: Changelog, add, tag_name: str, version_name: str):
    """
    Modify TAG on VERSION.

    VERSION is the name of a version to add tags to. If not given, the most recent version is used.
    """
    tag_name = tag_name.upper()
    try:
        if version_name:
            version = obj.get_version(version_name)
        else:
            version = obj.current_version()
    except KeyError as k:
        raise click.BadArgumentUsage(str(k))
    except ValueError as v:
        raise click.ClickException(str(v))

    if add:
        version.tags.append(tag_name)
    else:
        try:
            version.tags.remove(tag_name)
        except ValueError:
            raise click.BadArgumentUsage(f"Tag {tag_name} not found in version {version.name}.")

    obj.write()


@cli.command(short_help='Add entries to the changelog.')
@click.option('--bullet', '-b', 'bullets', metavar='TEXT', multiple=True, type=str, help='Add a bullet point.')
@click.option('--paragraph', '-p', 'paragraphs', metavar='TEXT', multiple=True, type=str, help='Add a paragraph')
@click.argument('section_name', metavar='SECTION', type=str, default='', required=False)
@click.argument('version_name', metavar='VERSION', type=str, default=None, required=False)
@click.pass_obj
def entry(obj: Changelog, bullets, paragraphs, section_name, version_name):
    """
    Add entries to SECTION in VERSION

    SECTION is the name of the section to append to. If not given, entries will be uncategorized.

    VERSION is the name of the version to append to. If not given, the most recent version will be used,
    or a new 'Unreleased' version will be added if the most recent version has been released.
    """

    section_name = section_name.title()
    try:
        if version_name:
            version = obj.get_version(version_name)
        else:
            version = obj.current_version(released=False, new_version=True)
    except KeyError as k:
        raise click.BadArgumentUsage(str(k))

    for p in paragraphs:
        version.add_entry(p, section_name)

    for b in bullets:
        version.add_entry('- ' + b, section_name)

    obj.write()
    count = len(paragraphs) + len(bullets)
    message = f"Created {count} {['entry', 'entries'][min(count - 1, 1)]}"
    if section_name:
        message += f" in section {click.style(section_name, fg='cyan')}"
    if version.name.lower() != 'unreleased':
        message += f" in version {click.style(version.name, fg='blue')}"
    click.echo(message)


@cli.command(short_help='Release versions.')
@click.option('-M', '--major', 'rel_seg', flag_value=0, type=int, default=None,
              help='Increment major version number.')
@click.option('-m', '--minor', 'rel_seg', flag_value=1, type=int,
              help='Increment minor version number.')
@click.option('-p', '--patch', 'rel_seg', flag_value=2, type=int,
              help='Increment patch number.')
@click.option('-s', '--segment', 'rel_seg', type=int,
              help='Increment nth segment of the version. For example, `--segment 2` is equivalent to `--patch`')
@click.option('-a', '--alpha', 'pre_seg', flag_value='a', type=str, default=None,
              help='Increment alpha version number.')
@click.option('-b', '--beta', 'pre_seg', flag_value='b', type=str,
              help='Increment beta version number.')
@click.option('-r', '--rc', 'pre_seg', flag_value='rc', type=str,
              help='Increment release candidate version number.')
@click.option('-f', '--full', 'pre_seg', flag_value='',
              help='Clear the prerelease value creating a full release.')
@click.option('-c', '--commit', is_flag=True,
              help='Create a git commit tagged with the new version number. '
                   'If there are no changes to commit, the current commit will be tagged instead.')
@click.option('-C', '--cargo', '-🦀', is_flag=True,
              help='Update the version in a Rust cargo.toml manifest file.')
@click.option('-y', '--yes', is_flag=True,
              help='Answer "yes" to all confirmation dialogs')
@click.option('-n', '--new', is_flag=True,
              help = 'Create a new version instead of renaming an existing one')
@click.argument('version_name', metavar='VERSION', type=str, default=None, required=False)
@click.pass_obj
def release(obj: Changelog, version_name, rel_seg, pre_seg, commit, cargo, yes, new):
    """
    Release VERSION, or a version incremented from the last release.

    VERSION is the name of the version to release. If VERSION is not provided but increment options are, then the most
    recent valid PEP440 version number is used instead.

    The most recent version in the log will be renamed (except by the --commit option) by using the VERSION as well as
    any increment options. Increment options will always reset the later segments, and prerelease increments will clear
    other kinds of prerelease.
    """

    if rel_seg is None and pre_seg is None and not version_name and not commit and not cargo:
        click.echo('Nothing to release!')
        raise click.Abort

    if new:
        cur_version = obj.add_version()
    else:
        cur_version = obj.current_version()
    old_name = cur_version.name

    if version_name:
        new_name = version_name
    else:
        for v in obj.versions:
            if v.version is not None:
                new_name = v.name
                break
        else:
            new_name = '0.0.0'

    if rel_seg is not None or pre_seg is not None:
        new_name = yaclog.version.increment_version(new_name, rel_seg, pre_seg)

    if new_name != old_name:
        if yaclog.version.is_release(old_name) and not yes:
            click.confirm(
            f"Rename release version {click.style(old_name, fg='blue')} "
            f"to {click.style(new_name, fg='blue')}?",
            abort=True)

        cur_version.name = new_name
        cur_version.date = datetime.datetime.utcnow().date()

        obj.write()
        click.echo(f"Renamed {click.style(old_name, fg='blue')} to {click.style(new_name, fg='blue')}")

    short_version, *_ = yaclog.version.extract_version(cur_version.name)
    if not short_version:
        short_version = cur_version.name.replace(' ', '-')

    if cargo:
        from ..cli import cargo_toml
        cargo_toml.set_version("Cargo.toml", str(short_version))
        click.echo("Updated Cargo.toml")

    if commit:
        import git
        repo = git.Repo(os.curdir)

        if repo.bare:
            raise click.BadOptionUsage('commit', f'Directory {os.path.abspath(os.curdir)} is not a git repo')

        repo.index.add(obj.path)

        if cargo:
            repo.index.add("Cargo.toml")

        tracked = len(repo.index.diff(repo.head.commit))
        untracked = len(repo.index.diff(None))

        message = [['Create tag', 'Commit and create tag'][min(tracked, 1)], 'for']

        if not cur_version.released:
            message.append('non-release')

        message.append(f"version {click.style(new_name, fg='blue')}?")

        if untracked > 0:
            message.append(click.style(
                f"You have {untracked} untracked file{'s'[:untracked]} that will not be included!",
                fg='red', bold=True))

        if not yes:
            click.confirm(' '.join(message), abort=True)

        if tracked > 0:
            commit = repo.index.commit(f'Release {cur_version.name}\n\n{cur_version.body()}')
            click.echo(f"Created commit {click.style(repo.head.commit.hexsha[0:7], fg='green')}")
        else:
            commit = repo.head.commit

        # noinspection PyTypeChecker
        repo_tag = repo.create_tag(short_version, ref=commit, message=cur_version.body(False))
        click.echo(f"Created tag {click.style(repo_tag.name, fg='green')}.")


if __name__ == '__main__':
    cli()
