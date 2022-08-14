#  yaclog: yet another changelog tool
#  Copyright (c) 2022. Andrew Cassidy
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

from tomlkit import dumps
from tomlkit import parse


def set_version(path, version):
    """
    Set the version string in a cargo.toml file

    :param path: path-like file location
    :param version: version string to overwrite with
    """
    with open(path, 'r+') as fp:
        toml = parse(fp.read())
        toml['package']['version'] = version
        fp.seek(0)
        fp.write(dumps(toml))
        fp.truncate()
