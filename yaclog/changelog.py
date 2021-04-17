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

    def __str__(self) -> str:
        if self.name.lower() == 'unreleased':
            return f'## {self.name}'

        date_str = self.date.isoformat() if self.date else 'UNKNOWN'
        line = f'## {self.name} - {date_str}'
        for tag in self.tags:
            line += ' [' + tag.upper() + ']'

        return line


class Changelog:
    def __init__(self, path: os.PathLike):
        self.path = path
        self.header = ''
        self.versions = []
        self.links = {}

        with open(path, 'r') as fp:
            # Read file
            line = fp.readline()
            while line and not line.startswith('##'):
                self.header += line
                line = fp.readline()

            version = None
            section = ''
            last_line = ''

            while line:
                if line.isspace():
                    # skip empty lines
                    pass
                elif match := re.fullmatch(
                        r'^##\s+(?P<name>\S*)(?:\s+-\s+(?P<date>\S+))?\s*?(?P<extra>.*?)\s*#*$', line):
                    # this is a version header in the form '## Name (- date) (tags*) (#*)'
                    version = VersionEntry()
                    section = ''

                    version.name, version.link, version.link_id = _strip_link(match['name'])

                    if match['date']:
                        try:
                            version.date = datetime.date.fromisoformat(match['date'].strip(string.punctuation))
                        except ValueError:
                            version.date = None

                    if match['extra']:
                        version.tags = [s.strip('[]') for s in re.findall(r'\[.*?]', match['extra'])]

                    self.versions.append(version)

                elif match := re.fullmatch(r'###\s+(\S*?)(\s+#*)?', line):
                    # this is a version section header in the form '### Name' or '### Name ###'
                    section = match[1].title()
                    if section not in version.sections.keys():
                        version.sections[section] = []

                elif match := re.fullmatch(r'\[(\S*)]:\s*(\S*)\n', line):
                    # this is a link definition in the form '[id]: link', so add it to the link table
                    self.links[match[1].lower()] = match[2]

                elif line[0] in bullets or last_line.isspace():
                    # bullet point or new paragraph
                    # bullet points are preserved since some people like to use '+', '-' or '*' for different things
                    version.sections[section].append(line.strip())

                else:
                    # not a bullet point, and no whitespace on last line, so append to the last entry
                    version.sections[section][-1] += '\n' + line.strip()

                last_line = line
                line = fp.readline()

            for version in self.versions:
                # handle links
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
