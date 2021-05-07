import datetime
import os.path
import textwrap

import yaclog.changelog

log_segments = [
    '# Changelog',

    'This changelog is for testing the parser, and has many things in it that might trip it up.',

    '## [Tests]',  # 2

    '- bullet point with no section',

    '### Bullet Points',  # 4

    textwrap.dedent('''\
    - bullet point dash
    * bullet point star
    + bullet point plus
      - sub point 1
      - sub point 2
      - sub point 3'''),

    '### Blocks ##',  # 6

    '#### This is an H4',
    '##### This is an H5',
    '###### This is an H6',

    '- this is a bullet point\nit spans many lines',

    'This is\na paragraph\nit spans many lines',

    '```python\nthis is some example code\nit spans many lines\n```',

    '> this is a block quote\nit spans many lines',

    '[FullVersion] - 1969-07-20 [TAG1] [TAG2]\n-----',  # 14
    '## Long Version Name',  # 15

    '[fullVersion]: http://endless.horse\n[id]: http://www.koalastothemax.com'
]

log_text = '\n\n'.join(log_segments)

log = yaclog.Changelog()
log.preamble = '# Changelog\n\n' \
               'This changelog is for testing the parser, and has many things in it that might trip it up.'
log.links = {'id': 'http://www.koalastothemax.com'}
log.versions = [yaclog.changelog.VersionEntry(), yaclog.changelog.VersionEntry(), yaclog.changelog.VersionEntry()]

log.versions[0].name = '[Tests]'
log.versions[0].sections = {
    '': ['- bullet point with no section'],
    'Bullet Points': [
        '- bullet point dash',
        '* bullet point star',
        '+ bullet point plus\n  - sub point 1\n  - sub point 2\n  - sub point 3'],
    'Blocks': [
        '#### This is an H4',
        '##### This is an H5',
        '###### This is an H6',

        '- this is a bullet point\nit spans many lines',

        'This is\na paragraph\nit spans many lines',

        '```python\nthis is some example code\nit spans many lines\n```',

        '> this is a block quote\nit spans many lines',
    ]
}

log.versions[1].name = 'FullVersion'
log.versions[1].link = 'http://endless.horse'
log.versions[1].tags = ['TAG1', 'TAG2']
log.versions[1].date = datetime.date.fromisoformat('1969-07-20')

log.versions[2].name = 'Long Version Name'
