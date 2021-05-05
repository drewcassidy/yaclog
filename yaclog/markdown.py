"""
Tools for parsing and manipulating markdown, including a very basic tokenizer.
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

import re
from typing import List

bullets = '+-*'
brackets = '[]'
code_regex = re.compile(r'^```')
header_regex = re.compile(r'^(?P<hashes>#+)\s+(?P<contents>[^#]+)(?:\s+#+)?$')
li_regex = re.compile(r'^[-+*] |\d+\. ')
numbered_regex = re.compile(r'^\d+\. ')
bullet_regex = re.compile(r'^[-+*] ')
link_id_regex = re.compile(r'^\[(?P<link_id>\S*)]:\s*(?P<link>.*)')
link_def_regex = re.compile(r'\[(?P<text>.*?)]\[(?P<link_id>.*?)]')  # deferred link in the form [name][id]
link_lit_regex = re.compile(r'\[(?P<text>.*?)]\((?P<link>.*?)\)')  # literal link in the form [name](url)

setext_h1_replace_regex = re.compile(r'(?<=\n)(?P<header>[^\n]+?)\n=+[ \t]*(?=\n)')
setext_h2_replace_regex = re.compile(r'(?<=\n)(?P<header>[^\n]+?)\n-+[ \t]*(?=\n)')


def strip_link(text):
    """
    Parses and removes any links from the input string

    :param text: An input string which may be a markdown link, either literal or an ID
    :return: A tuple of (name, url, id). If the input is not a link, it is returned verbatim as the name.
    """

    if link_lit := link_lit_regex.fullmatch(text):
        # in the form [name](link)
        return link_lit['text'], link_lit['link'], None

    if link_def := link_def_regex.fullmatch(text):
        # in the form [name][id] where id is hopefully linked somewhere else in the document
        return link_def['text'], None, link_def['link_id'].lower()

    return text, None, None


def join(segments: List[str]) -> str:
    """
    Joins multiple lines of markdown by adding double newlines between them, or a single newline between list items

    :param segments: A list of strings to join
    :return: A joined markdown string
    """

    text: List[str] = []
    last_segment = ''
    for segment in segments:
        if bullet_regex.match(segment) and bullet_regex.match(last_segment):
            pass
        elif numbered_regex.match(segment) and numbered_regex.match(last_segment):
            pass
        else:
            text.append('')

        text.append(segment)

        last_segment = segment

    return '\n'.join(text).strip()


class Token:
    """A single tokenized block of markdown, consisting of one or more lines of text."""

    def __init__(self, line_no: int, lines: List[str], kind: str):
        self.line_no = line_no
        """Which line this block appears on in the original file"""

        self.lines = lines
        """The lines of text making up this block"""

        self.kind = kind
        """What kind of token this is. One of ``h[1-6]``, ``p``, ``li`` or ``code``"""

    def __str__(self):
        return f'{self.kind}: {self.lines}'


def tokenize(text: str):
    """
    Tokenize a markdown string

    The tokenizer is very basic, and only cares about the highest-level blocks
    (Headers, top-level list items, links, code blocks, paragraphs).

    :param text: input text to tokenize
    :return: A list of tokens and a dictionary of links
    """

    # convert setext-style headers
    # The extra newline is to preserve line numbers
    text = setext_h1_replace_regex.sub(r'# \g<header>\n', text)
    text = setext_h2_replace_regex.sub(r'## \g<header>\n', text)

    lines = text.split('\n')
    tokens: List[Token] = []
    links = {}

    # state variables for parsing
    block = None

    for line_no, line in enumerate(lines):
        if block == 'code':
            # this is the contents of a code block
            assert block == tokens[-1].kind, 'block state variable in invalid state!'
            tokens[-1].lines.append(line)
            if code_regex.match(line):
                block = None

        elif code_regex.match(line):
            # this is the start of a code block
            tokens.append(Token(line_no, [line], 'code'))
            block = 'code'

        elif li_regex.match(line):
            # this is a list item
            tokens.append(Token(line_no, [line], 'li'))
            block = 'li'

        elif match := header_regex.match(line):
            # this is a header
            kind = f'h{len(match["hashes"])}'
            tokens.append(Token(line_no, [line], kind))

        elif match := link_id_regex.match(line):
            # this is a link definition in the form '[id]: link'
            links[match['link_id'].lower()] = match['link']
            block = None

        elif not line or line.isspace():
            # skip empty lines and reset block
            block = None

        elif block:
            # this is a line to be added to a paragraph or list item
            assert block == tokens[-1].kind, f'block state variable in invalid state! {block} != {tokens[-1].kind}'
            tokens[-1].lines.append(line)

        else:
            # this is a new paragraph
            tokens.append(Token(line_no, [line], 'p'))
            block = 'p'

    return tokens, links
