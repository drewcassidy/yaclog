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
import os
import re
import string
from typing import List, Tuple, Optional

bullets = '+-*'
brackets = '[]'


def _strip_link(token):
    if link_literal := re.fullmatch(r'\[(.*?)]\((.*?)\)', token):
        # in the form [name](link)
        return link_literal[1], link_literal[2], None

    if link_id := re.fullmatch(r'\[(.*?)]\[(.*?)]', token):
        # in the form [name][id] where id is hopefully linked somewhere else in the document
        return link_id[1], None, link_id[2].lower()

    return token, None, None


class VersionEntry:
    def __init__(self):
        self.sections = {'': []}
        self.name: str = ''
        self.date: Optional[datetime.date] = None
        self.tags: List[str] = []
        self.link: str = ''
        self.line_no = -1

    def __str__(self) -> str:
        if self.link:
            segments = [f'[{self.name}]']
        else:
            segments = [self.name]

        if self.date:
            segments += ['-', self.date.isoformat()]

        segments += [f'[{t.upper()}]' for t in self.tags]

        return ' '.join(segments)


class Changelog:
    def __init__(self, path: os.PathLike):
        self.path = path
        self.header = ''
        self.versions = []
        self.links = {}

        # Read file
        with open(path, 'r') as fp:
            self.lines = fp.readlines()

        section = ''
        in_block = False
        in_code = False

        # loop over lines in the file
        for line_no, line in enumerate(self.lines):
            if in_code:
                if re.match(r'^```', line):
                    line = '```'
                    in_code = False
                    in_block = False

                if len(self.versions) == 0:
                    self.header += line
                else:
                    self.versions[-1].sections[section][-1] += line

            elif re.match(r'^```', line):
                in_code = True
                if len(self.versions) == 0:
                    self.header += line
                else:
                    self.versions[-1].sections[section].append(line)

            elif match := re.fullmatch(
                    r'^##\s+(?P<name>\S*)(?:\s+-\s+(?P<date>\S+))?\s*?(?P<extra>.*?)\s*#*$', line):
                # this is a version header in the form '## Name (- date) (tags*) (#*)'
                section = ''
                in_block = False
                self._add_version_header(match['name'], match['date'], match['extra'], line_no)

            elif match := re.fullmatch(r'\[(\S*)]:\s*(\S*)\n', line):
                # this is a link definition in the form '[id]: link', so add it to the link table
                self.links[match[1].lower()] = match[2]

            elif len(self.versions) == 0:
                # we haven't encountered any version headers yet,
                # so its best to just add this line to the header string
                self.header += line

            elif line.isspace():
                # skip empty lines
                in_block = False
                pass

            elif match := re.fullmatch(r'###\s+(\S*?)(\s+#*)?', line):
                # this is a version section header in the form '### Name' or '### Name ###'
                section = match[1].title()
                if section not in self.versions[-1].sections.keys():
                    self.versions[-1].sections[section] = []
                in_block = False

            elif line[0] in '+-*#':
                # bullet point or subheader
                # subheaders are mostly preserved for round-trip accuracy, and are discouraged in favor of bullet points
                # bullet points are preserved since some people like to use '+', '-' or '*' for different things
                self.versions[-1].sections[section].append(line.strip())
                in_block = True

            elif in_block:
                # not a bullet point, header, etc, and in a block, so this line should be appended to the last
                self.versions[-1].sections[section][-1] += '\n' + line.strip()

            else:
                # not a bullet point, header, etc, and not in a block, so this is the start of a new paragraph
                self.versions[-1].sections[section].append(line.strip())
                in_block = True

        # handle links
        for version in self.versions:
            if match := re.fullmatch(r'\[(.*)]', version.name):
                # ref-matched link
                link_id = match[1].lower()
                if link_id in self.links:
                    version.link = self.links.pop(link_id)
                    version.link_id = None
                    version.name = match[1]

            elif version.link_id in self.links:
                # id-matched link
                version.link = self.links.pop(version.link_id)

        # strip whitespace from header
        self.header = self.header.strip()

    def write(self, path: os.PathLike = None):
        if path is None:
            path = self.path

        v_links = {}
        v_links.update(self.links)

        with open(path, 'w') as fp:
            fp.write(self.header)
            fp.write('\n\n')

            for version in self.versions:
                fp.write(f'## {version}\n\n')

                if version.link:
                    v_links[version.name] = version.link

                for section in version.sections:
                    if section:
                        fp.write(f'### {section}\n\n')

                    for entry in version.sections[section]:
                        fp.write(entry + '\n')
                        if entry[0] not in '-+*':
                            fp.write('\n')

                    if len(version.sections[section]) > 0:
                        fp.write('\n')

            for link_id, link in v_links.items():
                fp.write(f'[{link_id.lower()}]: {link}\n')

    def _add_version_header(self, name, date, extra, line_no):
        version = VersionEntry()

        version.name, version.link, version.link_id = _strip_link(name)
        version.line_no = line_no

        if date:
            try:
                version.date = datetime.date.fromisoformat(date.strip(string.punctuation))
            except ValueError:
                version.date = None

        if extra:
            version.tags = [s.strip('[]') for s in re.findall(r'\[.*?]', extra)]

        self.versions.append(version)


def read_version_header(line: str) -> Tuple[str, datetime.date, List[str]]:
    split = line.removeprefix('##').strip().split()
    name = split[0]
    date = datetime.date.fromisoformat(split[2]) if len(split) > 2 else None
    tags = [s.removeprefix('[').removesuffix(']') for s in split[3:]]

    return name, date, tags


def write_version_header(name: str, date: datetime.date, tags=None) -> str:
    line = f'## {name} - {date.isoformat()}'
    if tags:
        for tag in tags:
            line += ' [' + tag.upper() + ']'

    return line
