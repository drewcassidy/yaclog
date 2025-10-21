"""
Various helper functions for analyzing and manipulating :pep:`440` version numbers,
meant to augment the `packaging.version` module.
"""

#  Copyright 2025 Andrew Cassidy
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from typing import Optional, Tuple

from packaging.version import Version, VERSION_PATTERN

version_regex = re.compile(VERSION_PATTERN, re.VERBOSE | re.IGNORECASE)


def extract_version(version_str: str) -> Tuple[Optional[Version], int, int]:
    """
    Extracts a :pep:`440` version object from a string which may have other text

    :param version_str: The input string to extract from
    :return: A tuple of (version, start, end), where start and end are the span of the version in the original string
    """
    match = version_regex.search(version_str)
    if not match:
        return None, -1, -1
    return (Version(match[0]),) + match.span()


def increment_version(
    version_str: str, rel_seg: int = None, pre_seg: str = None
) -> str:
    """
    Increment the :pep:`440` version number in a string

    :param version_str: The input string to manipulate
    :param rel_seg: Which segment of the "release" value to increment, if any
    :param pre_seg: Which kind of prerelease to use, if any. An empty string clears the prerelease field.
    :return: The original string with the version number incremented
    """
    v, *span = extract_version(version_str)
    epoch = v.epoch
    release = v.release
    pre = v.pre
    post = v.post
    dev = v.dev
    local = v.local

    if rel_seg is not None:
        if len(release) <= rel_seg:
            release += (0,) * (1 + rel_seg - len(release))
        release = (
            release[0:rel_seg]
            + (release[rel_seg] + 1,)
            + (0,) * (len(release) - rel_seg - 1)
        )
        pre = None

    if pre_seg is not None:
        if pre_seg == "":  # full release, clear prerelease field
            pre = None
        elif pre and pre[0] == pre_seg:  # increment current prerelease type
            pre = (pre_seg, pre[1] + 1)
        else:
            pre = (pre_seg, 1)  # set prerelease field

    new_v = join_version(epoch, release, pre, post, dev, local)
    return version_str[0 : span[0]] + new_v + version_str[span[1] :]


def join_version(epoch, release, pre, post, dev, local) -> str:
    """Join multiple segments of a :pep:`440` version"""
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


def is_release(version_str: str) -> bool:
    """
    Check if a version string is a release version

    :param version_str: the input string to check
    :return: True if the input contains a released :pep:`440` version,
        or False if a prerelease version or no version is found
    """
    v, *span = extract_version(version_str)
    if v:
        return not (v.is_devrelease or v.is_prerelease)
    else:
        return False
