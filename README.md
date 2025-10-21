# Yaclog: Yet Another Commandline Changelog Tool

[![Documentation Status](https://readthedocs.org/projects/yaclog/badge/?version=latest)](https://yaclog.readthedocs.io/en/)
[![CI Status](https://git.offworldcolonies.nexus/drewcassidy/yaclog/badges/workflows/build.yml/badge.svg?branch=main&label=build)](https://git.offworldcolonies.nexus/drewcassidy/yaclog/actions)
[![PyPI version](https://badge.fury.io/py/yaclog.svg)](https://pypi.org/project/yaclog/)

Yaclog is a python library and command line tool to make it easier to keep track of changes to your projects. It includes commands for appending new changes to a markdown changelog file, as well as releasing new versions for deployment via git tags.

![a yak who is a log](https://git.offworldcolonies.nexus/drewcassidy/yaclog/raw/branch/main/logo.png)

*Logo by Erin Cassidy*

## Installation

Install and update using [pip](https://pip.pypa.io/en/stable/quickstart/):

```shell
$ pip install -U yaclog
```

## Usage

For usage from the command line, yaclog provides the `yaclog` command:
```
Usage: yaclog [OPTIONS] COMMAND [ARGS]...

  Manipulate markdown changelog files.

Options:
  --path FILE  Location of the changelog file.  [default: CHANGELOG.md]
  --version    Show the version and exit.
  --help       Show this message and exit.

Commands:
  entry    Add entries to the changelog.
  format   Reformat the changelog file.
  init     Create a new changelog file.
  release  Release versions.
  show     Show changes from the changelog file
  tag      Modify version tags
```

### Example workflow

Create a new changelog:
```shell
$ yaclog init
```

Add some new entries to the current unreleased version:
```shell
$ yaclog entry -b 'Introduced some more bugs'
$ yaclog entry -b 'Introduced some more features'
```

Show the current version:

```shell
$ yaclog show
```
```
Unreleased

- Introduced some more bugs
- Introduced some more features
```

Release the current version and make a git tag for it

```shell
$ yaclog release 0.0.1 -c
```
```
Renamed version "Unreleased" to "0.0.1".
Commit and create tag for version 0.0.1? [y/N]: y
Created commit a7b6789
Created tag "0.0.1".
```
