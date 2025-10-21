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

from tomlkit import dumps
from tomlkit import parse


def set_version(path, version):
    """
    Set the version string in a cargo.toml file

    :param path: path-like file location
    :param version: version string to overwrite with
    """
    with open(path, "r+") as fp:
        toml = parse(fp.read())
        toml["package"]["version"] = version
        fp.seek(0)
        fp.write(dumps(toml))
        fp.truncate()
