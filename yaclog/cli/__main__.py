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
@click.option('--path', envvar='YACLOG_PATH', default='CHANGELOG.md',
              type=click.Path(dir_okay=False, writable=True, readable=True))
@click.version_option()
@click.pass_context
def cli(ctx, path):
    ctx.obj = path

    if not (ctx.invoked_subcommand == 'init' or os.path.exists(path)):
        # if the path doesnt exist, then ask if we can create it
        if click.confirm(f'Changelog file {path} does not exist. Would you like to create it?'):
            ctx.invoke('init')
        else:
            return


@cli.command('init')
@click.pass_context
def init(ctx):
    path = ctx.parent.params['path']

    if os.path.exists(path) and not click.confirm(
            f'Changelog file {path} already exists. Would you like to overwrite it?'):
        return

    yaclog.Changelog(path).write()
    print(f'Created new changelog file at {path}')


if __name__ == '__main__':
    cli()
