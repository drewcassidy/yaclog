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
from typing import List, Tuple, Optional

bullets = '+-*'
brackets = '[]'

code_regex = re.compile(r'^```')
header_regex = re.compile(r'^(?P<hashes>#+)\s+(?P<contents>[^#]+)(?:\s+#+)?$')
under1_regex = re.compile(r'^=+\s*$')
under2_regex = re.compile(r'^-+\s*$')
bullet_regex = re.compile(r'^[-+*]')
linkid_regex = re.compile(r'^\[(?P<link_id>\S*)]:\s*(?P<link>.*)')

default_header = '# Changelog\n\nAll notable changes to this project will be documented in this file'


def _strip_link(token):
    if link_literal := re.fullmatch(r'\[(.*?)]\((.*?)\)', token):
        # in the form [name](link)
        return link_literal[1], link_literal[2], None

    if link_id := re.fullmatch(r'\[(.*?)]\[(.*?)]', token):
        # in the form [name][id] where id is hopefully linked somewhere else in the document
        return link_id[1], None, link_id[2].lower()

    return token, None, None


def _join_markdown(segments: List[str]) -> str:
    text: List[str] = []
    last_bullet = False
    for segment in segments:
        is_bullet = bullet_regex.match(segment)

        if not is_bullet or not last_bullet:
            text.append('')

        text.append(segment)

        last_bullet = is_bullet

    return '\n'.join(text).strip()


class VersionEntry:
    def __init__(self):
        self.sections = {'': []}
        self.name: str = 'Unreleased'
        self.date: Optional[datetime.date] = None
        self.tags: List[str] = []
        self.link: Optional[str] = None
        self.link_id: Optional[str] = None
        self.line_no: int = -1

    def body(self, md: bool = True) -> str:
        segments = []

        for section, entries in self.sections.items():
            if section:
                if md:
                    segments.append(f'### {section.title()}')
                else:
                    segments.append(f'{section.upper()}:')

            if len(entries) > 0:
                segments.append(_join_markdown(entries))

        return _join_markdown(segments)

    def header(self, md: bool = True) -> str:
        segments = []

        if md:
            segments.append('##')

        if self.link and md:
            segments.append(f'[{self.name}]')
        else:
            segments.append(self.name)

        if self.date or len(self.tags) > 0:
            segments.append('-')

        if self.date:
            segments.append(self.date.isoformat())

        segments += [f'[{t.upper()}]' for t in self.tags]

        return ' '.join(segments)

    def text(self, md: bool = True) -> str:
        return self.header(md) + '\n\n' + self.body(md)

    def __str__(self) -> str:
        return self.header(False)


class Changelog:
    def __init__(self, path=None):
        self.path: os.PathLike = path
        self.header: str = ''
        self.versions: List[VersionEntry] = []
        self.links = {}

        if not path or not os.path.exists(path):
            self.header = default_header
            return

        # Read file
        with open(path, 'r') as fp:
            lines = fp.readlines()

        section = ''
        in_block = False
        in_code = False

        segments: List[Tuple[int, List[str], str]] = []
        header_segments = []

        for line_no, line in enumerate(lines):
            if in_code:
                # this is the contents of a code block
                segments[-1][1].append(line)
                if code_regex.match(line):
                    in_code = False
                    in_block = False

            elif code_regex.match(line):
                # this is the start of a code block
                in_code = True
                segments.append((line_no, [line], 'code'))

            elif under1_regex.match(line) and in_block and len(segments[-1][1]) == 1 and segments[-1][2] == 'p':
                # this is an underline for a setext-style H1
                # ugly but it works
                last = segments.pop()
                segments.append((last[0], last[1] + [line], 'h1'))

            elif under2_regex.match(line) and in_block and len(segments[-1][1]) == 1 and segments[-1][2] == 'p':
                # this is an underline for a setext-style H2
                # ugly but it works
                last = segments.pop()
                segments.append((last[0], last[1] + [line], 'h2'))

            elif bullet_regex.match(line):
                in_block = True
                segments.append((line_no, [line], 'li'))

            elif match := header_regex.match(line):
                # this is a header
                kind = f'h{len(match["hashes"])}'
                segments.append((line_no, [line], kind))
                in_block = False

            elif match := linkid_regex.match(line):
                # this is a link definition in the form '[id]: link', so add it to the link table
                self.links[match['link_id'].lower()] = match['link']

            elif line.isspace():
                # skip empty lines
                in_block = False

            elif in_block:
                # this is a line to be added to a paragraph
                segments[-1][1].append(line)
            else:
                # this is a new paragraph
                in_block = True
                segments.append((line_no, [line], 'p'))

        for segment in segments:
            text = ''.join(segment[1]).strip()

            if segment[2] == 'h2':
                # start of a version

                slug = text.rstrip('-').strip('#').strip()
                split = slug.split()
                if '-' in split:
                    split.remove('-')

                version = VersionEntry()
                section = ''

                version.name = slug
                version.line_no = segment[0]
                tags = []
                date = None

                for word in split[1:]:
                    if match := re.match(r'\d{4}-\d{2}-\d{2}', word):
                        # date
                        try:
                            date = datetime.date.fromisoformat(match[0])
                        except ValueError:
                            break
                    elif match := re.match(r'^\[(?P<tag>\S*)]', word):
                        tags.append(match['tag'])
                    else:
                        break

                else:
                    # matches the schema
                    version.name, version.link, version.link_id = _strip_link(split[0])
                    version.date = date
                    version.tags = tags

                self.versions.append(version)

            elif len(self.versions) == 0:
                # we haven't encountered any version headers yet,
                # so its best to just add this line to the header string
                header_segments.append(text)

            elif segment[2] == 'h3':
                # start of a version section
                section = text.strip('#').strip()
                if section not in self.versions[-1].sections.keys():
                    self.versions[-1].sections[section] = []

            else:
                # change log entry
                self.versions[-1].sections[section].append(text)

        # handle links
        for version in self.versions:
            if match := re.fullmatch(r'\[(.*)]', version.name):
                # ref-matched link
                link_id = match[1].lower()
                if link_id in self.links:
                    version.link = self.links[link_id]
                    version.link_id = None
                    version.name = match[1]

            elif version.link_id in self.links:
                # id-matched link
                version.link = self.links[version.link_id]

        # strip whitespace from header
        self.header = _join_markdown(header_segments)

    def write(self, path: os.PathLike = None):
        if path is None:
            path = self.path

        segments = [self.header]
        v_links = {**self.links}

        for version in self.versions:
            if version.link:
                v_links[version.name.lower()] = version.link

            segments.append(version.text())

        segments += [f'[{link_id}]: {link}' for link_id, link in v_links.items()]

        text = _join_markdown(segments)

        with open(path, 'w') as fp:
            fp.write(text)
