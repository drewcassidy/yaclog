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

import click
import os.path
import datetime
import yaclog.cli.version_util
from yaclog import Changelog


@click.group()
@click.option('--path', envvar='YACLOG_PATH', default='CHANGELOG.md', show_default=True,
              type=click.Path(dir_okay=False, writable=True, readable=True),
              help='Location of the changelog file.')
@click.version_option()
@click.pass_context
def cli(ctx, path):
    """Manipulate markdown changelog files."""
    if not (ctx.invoked_subcommand == 'init') and not os.path.exists(path):
        # file does not exist and this isn't the init command
        raise click.FileError(f'Changelog file {path} does not exist. Create it by running `yaclog init`.')

    ctx.obj = yaclog.read(path)


@cli.command()
@click.pass_obj
def init(obj: Changelog):
    """Create a new changelog file."""
    if os.path.exists(obj.path):
        click.confirm(f'Changelog file {obj.path} already exists. Would you like to overwrite it?', abort=True)
        os.remove(obj.path)

    yaclog.Changelog(obj.path).write()
    print(f'Created new changelog file at {obj.path}')


@cli.command('format')  # dont accidentally hide the `format` python builtin
@click.pass_obj
def reformat(obj: Changelog):
    """Reformat the changelog file."""
    obj.write()
    print(f'Reformatted changelog file at {obj.path}')


@cli.command(short_help='Show changes from the changelog file')
@click.option('--all', '-a', 'all_versions', is_flag=True, help='Show the entire changelog.')
@click.argument('versions', type=str, nargs=-1)
@click.pass_obj
def show(obj: Changelog, all_versions, versions):
    """Show the changes for VERSIONS.

    VERSIONS is a list of versions to print. If not given, the most recent version is used.
    """
    if all_versions:
        with open(obj.path, 'r') as fp:
            click.echo_via_pager(fp.read())
    else:
        if len(versions):
            v_list = []
            for v_name in versions:
                matches = [v for v in obj.versions if v.name == v_name]
                if len(matches) == 0:
                    raise click.BadArgumentUsage(f'Version "{v_name}" not found in changelog.')
                v_list += matches
        else:
            v_list = [obj.versions[0]]

        for v in v_list:
            click.echo(v.text(False))


@cli.command(short_help='Modify version tags')
@click.option('--add/--delete', '-a/-d', default=True, is_flag=True, help='Add or delete tags')
@click.argument('tag_name', metavar='tag', type=str)
@click.argument('version_name', metavar='version', type=str, required=False)
@click.pass_obj
def tag(obj: Changelog, add, tag_name: str, version_name: str):
    """Modify TAG on VERSION.

    VERSION is the name of a version to add tags to. If not given, the most recent version is used.
    """
    tag_name = tag_name.upper()
    if version_name:
        matches = [v for v in obj.versions if v.name == version_name]
        if len(matches) == 0:
            raise click.BadArgumentUsage(f'Version "{version_name}" not found in changelog.')
        version = matches[0]
    else:
        version = obj.versions[0]

    if add:
        version.tags.append(tag_name)
    else:
        try:
            version.tags.remove(tag_name)
        except ValueError:
            raise click.BadArgumentUsage(f'Tag "{tag_name}" not found in version "{version.name}".')

    obj.write()


@cli.command(short_help='Add entries to the changelog.')
@click.option('--bullet', '-b', 'bullets', multiple=True, type=str,
              help='Bullet points to add. '
                   'When multiple bullet points are provided, additional points are added as sub-points.')
@click.option('--paragraph', '-p', 'paragraphs', multiple=True, type=str,
              help='Paragraphs to add')
@click.argument('section_name', metavar='SECTION', type=str, default='', required=False)
@click.argument('version_name', metavar='VERSION', type=str, default=None, required=False)
@click.pass_obj
def entry(obj: Changelog, bullets, paragraphs, section_name, version_name):
    """Add entries to SECTION in VERSION

    SECTION is the name of the section to append to. If not given, entries will be uncategorized.

    VERSION is the name of the version to append to. If not given, the most recent version will be used,
    or a new 'Unreleased' version will be added if the most recent version has been released.
    """

    section_name = section_name.title()
    if version_name:
        matches = [v for v in obj.versions if v.name == version_name]
        if len(matches) == 0:
            raise click.BadArgumentUsage(f'Version "{version_name}" not found in changelog.')
        version = matches[0]
    else:
        version = obj.versions[0]
        if version.name.lower() != 'unreleased':
            version = yaclog.changelog.VersionEntry()
            obj.versions.insert(0, version)

    if section_name not in version.sections.keys():
        version.sections[section_name] = []

    section = version.sections[section_name]
    section += paragraphs

    sub_bullet = False
    bullet_str = ''
    for bullet in bullets:
        bullet = bullet.strip()
        if bullet[0] not in ['-+*']:
            bullet = '- ' + bullet

        if sub_bullet:
            bullet = '\n    ' + bullet

        bullet_str += bullet
        sub_bullet = True
    section.append(bullet_str)

    obj.write()


@cli.command()
@click.option('-v', '--version', 'v_flag', type=str, help='The full version string to release.')
@click.option('-M', '--major', 'v_flag', flag_value='+M', help='Increment major version number.')
@click.option('-m', '--minor', 'v_flag', flag_value='+m', help='Increment minor version number.')
@click.option('-p', '--patch', 'v_flag', flag_value='+p', help='Increment patch number.')
@click.option('-a', '--alpha', 'v_flag', flag_value='+a', help='Increment alpha version number.')
@click.option('-b', '--beta', 'v_flag', flag_value='+b', help='Increment beta version number.')
@click.option('-r', '--rc', 'v_flag', flag_value='+rc', help='Increment release candidate version number.')
@click.option('-c', '--commit', help='Create a git commit tagged with the new version number.')
@click.pass_obj
def release(obj: Changelog, v_flag, commit):
    version = [v for v in obj.versions if v.name.lower() != 'unreleased'][0]
    cur_version = obj.versions[0]

    if v_flag[0] == '+':
        new_name = yaclog.cli.version_util.increment_version(version.name, v_flag)
    else:
        new_name = v_flag

    if yaclog.cli.version_util.is_release(cur_version.name):
        click.confirm(f'Rename release version "{cur_version.name}" to "{new_name}"?', abort=True)

    cur_version.date = datetime.datetime.utcnow().date()

    obj.write()


if __name__ == '__main__':
    cli()
