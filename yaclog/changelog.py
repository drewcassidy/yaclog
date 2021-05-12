"""
Contains the `Changelog` class that represents a parsed changelog file that can be read from and written to
disk as markdown, as well as the `VersionEntry` class that represents a single version within that changelog.
"""

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

from __future__ import annotations

import datetime
import os
import re
from typing import List, Optional, Dict

import click  # only for styling

import yaclog.markdown as markdown
import yaclog.version


class VersionEntry:
    """
    A serialized representation of a single version entry in a `Changelog`,
    containing the changes made since the previous version
    """

    _header_regex = re.compile(  # THE LANGUAGE OF THE GODS
        r"##\s+(?P<name>.*?)(?:\s+-)?(?:\s+(?P<date>\d{4}-\d{2}-\d{2}))?(?P<tags>(?:\s+\[[^]]*?])*)\s*$")

    _tag_regex = re.compile(r'\[(?P<tag>[^]]*?)]')

    def __init__(self, name: str = 'Unreleased',
                 date: Optional[datetime.date] = None, tags: Optional[List[str]] = None,
                 link: Optional[str] = None, link_id: Optional[str] = None, line_no: Optional[int] = None):
        """
        :param str name: The version's name
        :param Optional[datetime.date] date: When the version was released
        :param tags: The version's tags
        :param link: The version's URL
        :param link_id: The version's link ID
        :param line_no: What line in the original file the version starts on
        """

        self.name: str = name
        """The version's name"""

        self.date: Optional[datetime.date] = date
        """When the version was released"""

        self.tags: List[str] = tags if tags else []
        """The version's tags"""

        self.link: Optional[str] = link
        """The version's URL"""

        self.link_id: Optional[str] = link_id
        """The version's link ID, uses the version name by default when writing"""

        self.line_no: Optional[int] = line_no
        """What line the version occurs at in the file, or `None` if the version was not read from a file. 
        This is not guaranteed to be correct after the changelog has been modified, 
        and it has no effect on the written file"""

        self.sections: Dict[str, List[str]] = {'': []}
        """The dictionary of change entries in the version, organized by section. 
        Uncategorized changes have a section of an empty string."""

    @classmethod
    def from_header(cls, header: str, line_no: Optional[int] = None) -> VersionEntry:
        """
        Create a new version entry from a markdown header

        :param header: A markdown header to parse
        :param line_no: Line number the header is on
        :return: a new VersionEntry with the header's information
        """
        version = cls(line_no=line_no)

        match = cls._header_regex.match(header)
        assert match, f'failed to parse version header: "{header}"'

        version.name, version.link, version.link_id = markdown.strip_link(match['name'])

        if match['date']:
            try:
                version.date = datetime.date.fromisoformat(match['date'])
            except ValueError:
                return cls(name=header.lstrip('#').strip(), line_no=line_no)

        if match['tags']:
            version.tags = [m['tag'].upper() for m in cls._tag_regex.finditer(match['tags'])]

        return version

    def add_entry(self, contents: str, section: str = '') -> None:
        """
        Add a new entry to the version

        :param contents: The contents string to add
        :param section: Which section to add to.
        """

        section = section.title()
        if section not in self.sections.keys():
            self.sections[section] = []

        self.sections[section].append(contents)

    def body(self, md: bool = True, color: bool = False) -> str:
        """
        Get the version's body as a string

        :param md: Format headings as markdown
        :param color: Add color codes to the string for display in a terminal
        :return: The formatted version body, without the version header
        """

        segments = []

        for section, entries in self.sections.items():
            if section:
                if md:
                    prefix = '### '
                    title = section.title()
                else:
                    prefix = ''
                    title = section.upper()

                if color:
                    prefix = click.style(prefix, fg='bright_black')
                    title = click.style(title, fg='cyan', bold=True)

                segments.append(prefix + title)

            if len(entries) > 0:
                segments += entries

        return markdown.join(segments)

    def header(self, md: bool = True, color: bool = False) -> str:
        """
        Get the version's header as a string

        :param md: Format headings as markdown
        :param color: Add color codes to the string for display in a terminal
        :return: The formatted version header
        """

        if md:
            prefix = '## '
        else:
            prefix = ''

        segments = []

        if self.link and md:
            segments.append(f'[{self.name}]')
        else:
            segments.append(self.name)

        if self.date or len(self.tags) > 0:
            segments.append('-')

        if self.date:
            segments.append(self.date.isoformat())

        segments += [f'[{t.upper()}]' for t in self.tags]

        title = ' '.join(segments)

        if color:
            prefix = click.style(prefix, fg='bright_black')
            title = click.style(title, fg='blue', bold=True)

        return prefix + title

    def text(self, md: bool = True, color: bool = False) -> str:
        """
        Get the version's contents as a string

        :param md: Format headings as markdown
        :param color: Add color codes to the string for display in a terminal
        :return: The formatted version header and body
        """

        contents = self.header(md, color)
        body = self.body(md, color)
        if body:
            contents += '\n\n' + body
        return contents

    @property
    def released(self) -> bool:
        """Returns true if a PEP440 version number is present in the version name, and has no prerelease segments"""
        return yaclog.version.is_release(self.name)

    @property
    def version(self):
        """Returns the PEP440 version number from the version name, or `None` if none is found"""
        return yaclog.version.extract_version(self.name)[0]

    def __str__(self) -> str:
        return self.header(False)


class Changelog:
    """
    A serialized representation of a Markdown changelog made up of a preamble, multiple versions, and a link table.
    """

    def __init__(self, path=None,
                 preamble: str = "# Changelog\n\nAll notable changes to this project will be documented in this file"):
        """
        Contents will be automatically read from disk if the file exists

        :param path: The changelog's path on disk.
        :param str preamble: The changelog preamble to use if the file does not exist.
        """
        self.path = os.path.abspath(path) if path else None
        """The path of the changelog's file on disk"""

        self.preamble: str = preamble
        """Any text at the top of the changelog before any version information, including the title.
        It can contain the title, an explanation of the file's purpose, as well as any general machine-readable 
        information for use with other tools."""

        self.versions: List[VersionEntry] = []
        """A list of versions in the changelog, with the most recent version first"""

        self.links: Dict[str, str] = {}
        """Link definitions at the end of the changelog, as a dictionary of ``{id: url}``"""

        if path and os.path.exists(path):
            self.read()

    def read(self, path=None) -> None:
        """
        Read a markdown changelog file from disk. The object's contents will be overwritten by the file contents if
        reading is successful.

        :param path: The changelog's path on disk. By default, :py:attr:`~Changelog.path` is used
        """

        if not path:
            # use the object path if none was provided
            path = self.path

        # Read file
        with open(path, 'r') as fp:
            tokens, links = markdown.tokenize(fp.read())

        section = ''
        versions = []
        preamble_segments = []

        for token in tokens:
            text = '\n'.join(token.lines)

            if token.kind == 'h2':
                # start of a version
                versions.append(VersionEntry.from_header(text, line_no=token.line_no))
                section = ''

            elif len(versions) == 0:
                # we haven't encountered any version headers yet,
                # so its best to just add this line to the preamble
                preamble_segments.append(text)

            elif token.kind == 'h3':
                # start of a version section
                section = text.strip('#').strip()
                if section not in versions[-1].sections.keys():
                    versions[-1].sections[section] = []

            else:
                # change log entry
                versions[-1].sections[section].append(text)

        # handle links
        for version in versions:
            if match := re.fullmatch(r'\[(.*)]', version.name):
                # ref-matched link
                link_id = match[1].lower()
                if link_id in links:
                    version.link = links[link_id]
                    version.link_id = None
                    version.name = match[1]

            elif version.link_id in links:
                # id-matched link
                version.link = links[version.link_id]

        self.preamble = markdown.join(preamble_segments)
        self.versions = versions
        self.links = links

    def write(self, path=None) -> None:
        """
        Write a changelog to a Markdown file.

        :param path: The changelog's path on disk. By default, :py:attr:`~Changelog.path` is used.
        """

        if path is None:
            # use the object path if none was provided
            path = self.path

        segments = []

        if self.preamble:
            segments.append(self.preamble)

        v_links = {**self.links}

        for version in self.versions:
            if version.link:
                v_links[version.name.lower()] = version.link

            segments.append(version.text() + '\n')

        segments += [f'[{link_id}]: {link}' for link_id, link in v_links.items()]

        text = markdown.join(segments)

        with open(path, 'w') as fp:
            fp.write(text)

    def add_version(self, index: int = 0, *args, **kwargs) -> VersionEntry:
        """
        Add a new version to the changelog

        :param index: Where to add the new version in the log. Defaults to the top
        :param args: args to forward to the :py:class:`VersionEntry` constructor
        :param kwargs: kwargs to forward to the :py:class:`VersionEntry` constructor
        :return: The created entry
        """
        self.versions.insert(index, version := VersionEntry(*args, **kwargs))
        return version

    def current_version(self, released: Optional[bool] = None, new_version: bool = False,
                        new_version_name: str = 'Unreleased') -> VersionEntry:
        """
        Get the current version from the changelog

        :param released: if the returned version should be a released version,
            an unreleased version, or `None` to return the most recent
        :param new_version: if a new version should be created if none exist.
        :param new_version_name: The name of the version to create if there
            are no matches and ``new_version`` is True.
        :return: The current version matching the criteria,
            or `None` if ``new_version`` is disabled and none are found.
        """

        # return the first version that matches `released`
        for version in self.versions:
            if version.released == released or released is None:
                return version

        # fallback if none are found
        if new_version:
            return self.add_version(name=new_version_name)
        else:
            if released is not None:
                raise ValueError(f'Changelog has no current version matching released={released}')
            else:
                raise ValueError('Changelog has no current version')

    def get_version(self, name: Optional[str] = None) -> VersionEntry:
        """
        Get a version from the changelog by name.

        :param name: The name of the version to get, or `None` to return the most recent.
            The first version with this value in its name is returned.
        :return: The first version with the selected name
        """

        for version in self.versions:
            if name in version.name or name is None:
                return version
        raise KeyError(f'Version {name} not found in changelog')

    def __getitem__(self, item: str) -> VersionEntry:
        return self.get_version(item)

    def __len__(self) -> int:
        return len(self.versions)
