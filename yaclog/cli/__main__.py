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
import yaclog
import os.path


@click.group()
@click.option('--path', envvar='YACLOG_PATH', default='CHANGELOG.md', show_default=True,
              type=click.Path(dir_okay=False, writable=True, readable=True),
              help='Location for the changelog file')
@click.version_option()
@click.pass_context
def cli(ctx, path):
    """Manipulate markdown changelog files"""
    if not (ctx.invoked_subcommand == 'init' or os.path.exists(path)):
        # if the path doesnt exist, then ask if we can create it
        if click.confirm(f'Changelog file {path} does not exist. Would you like to create it?', abort=True):
            ctx.invoke('init')

    ctx.obj = yaclog.read(path)


@cli.command()
@click.pass_context
def init(ctx):
    """Create a new changelog file"""
    path = ctx.parent.params['path']

    if os.path.exists(path):
        click.confirm(f'Changelog file {path} already exists. Would you like to overwrite it?', abort=True)

    yaclog.Changelog(path).write()
    print(f'Created new changelog file at {path}')


@cli.command('format')
@click.pass_obj
def reformat(obj: yaclog.Changelog):
    """Reformat the changelog file"""
    obj.write()
    print(f'Reformatted changelog file at {obj.path}')


@cli.command(short_help='Show changes from the changelog file')
@click.option('--all', '-a', 'all_versions', is_flag=True, help='show all versions')
@click.argument('versions', type=str, nargs=-1)
@click.pass_obj
def show(obj: yaclog.Changelog, all_versions, versions):
    """Show the changes for VERSIONS

    VERSIONS is a list of versions to print. If not given, the most recent version is used
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
                    raise click.BadArgumentUsage(f'version "{v_name}" not found in changelog')
                v_list += matches
        else:
            v_list = [obj.versions[0]]

        for v in v_list:
            click.echo(v.text())


if __name__ == '__main__':
    cli()
