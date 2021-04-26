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

from packaging.version import Version, InvalidVersion


def is_release(version: str) -> bool:
    try:
        v = Version(version)
        return not (v.is_devrelease or v.is_prerelease)
    except InvalidVersion:
        return False


def increment_version(version: str, mode: str) -> str:
    v = Version(version)
    epoch = v.epoch
    release = v.release
    pre = v.pre
    post = v.post
    dev = v.dev
    local = v.local

    if mode == '+M':
        release = (release[0] + 1,) + ((0,) * len(release[1:]))
        pre = post = dev = None
    elif mode == '+m':
        release = (release[0], release[1] + 1) + ((0,) * len(release[2:]))
        pre = post = dev = None
    elif mode == '+p':
        release = (release[0], release[1], release[2] + 1) + ((0,) * len(release[3:]))
        pre = post = dev = None
    elif mode in ['+a', '+b', '+rc']:
        if pre[0] == mode[1:]:
            pre = (mode[1:], pre[1] + 1)
        else:
            pre = (mode[1:], 0)
    else:
        raise IndexError(f'Unknown mode {mode}')

    return join_version(epoch, release, pre, post, dev, local)


def join_version(epoch, release, pre, post, dev, local) -> str:
    parts = []

    # Epoch
    if epoch != 0:
        parts.append(f"{epoch}!")

    # Release segment
    parts.append(".".join(str(x) for x in release))

    # Pre-release
    if pre is not None:
        parts.append("".join(str(x) for x in pre))

    # Post-release
    if post is not None:
        parts.append(f".post{post}")

    # Development release
    if dev is not None:
        parts.append(f".dev{dev}")

    # Local version segment
    if local is not None:
        parts.append(f"+{local}")

    return "".join(parts)
