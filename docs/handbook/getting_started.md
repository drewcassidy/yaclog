# Getting Started

## Installation

Install and update using [pip](https://pip.pypa.io/en/stable/quickstart/):

```shell
$ pip install -U yaclog
```

## Usage

For detailed documentation on the {command}`yaclog` command and its subcommands see the {doc}`commands`.

### Example workflow

Create a new changelog in the current directory:
```shell
$ yaclog init
```

Add some new entries to the "Added" section of the current unreleased version:
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
