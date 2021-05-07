# Changelog Files

Yaclog works on Markdown changelog files, using a machine-readable format based on what is proposed by [Keep a Changelog](https://keepachangelog.com). Changelog files can be created using the {command}`yaclog init` command.

## Preamble

The preamble is the text at the top of the file before any version information. It can contain the title, an explanation of the file's purpose, as well as any general machine-readable information you may want to include for use with other tools. Yaclog does not provide any ways to manipulate the front matter from the command line due to its open-ended nature.

## Versions

Version information begins with a header, which is an H2 containing the version's name, as well as optionally the date in ISO-8601 form, and any tag metadata. Some example version headers:

```markdown
## 1.0.0
```

```markdown
## 3.2.0 "Columbia" - 1981-07-20
```

```markdown
## Version 8.0.0rc1 1988-11-15 [PRERELEASE]
```

Version names should (but are not required to) include a version number in {pep}`440` format, which is a superset of [semantic versioning](https://semver.org). Versions can be incremented or renamed using the {command}`yaclog release` command.

## Entries

Entries are individual changes made since the previous version. They can be paragraphs, list items, or any markdown block element. Entries can be either uncategorized, or organized into sections using H3 headers. Entries can be added using the {command}`yaclog entry` command.

## Tags

Tags are additional metadata added to a version header, denoted by all-caps text surrounded in square brackets. Tags can be used to mark that a version is a prerelease, that it has been yanked for security reasons, or for marking compatibility with some other piece of software. Tags can be added and removed using the {command}`yaclog tag` command.

## Example

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## 0.13.0 "Aquarius" - 1970-04-11 [YANKED]

Yanked due to issues with oxygen tanks, currently investigating

### Added

- Extra propellant in preparation for future versions

### Changed

- Replaced Ken Mattingly
- Stirred oxygen tanks

## 0.12.0 "Intrepid" - 1969-11-14

### Added

- New ALSEP package for surface science
- Color cameras
- Surface rendezvous with Surveyor 3

### Fixed

- 1201/1202 alarm distracting crew during landing

### Known Issues

- Lightning strike during launch: No effect on performance

## 0.11.0 "Eagle" - 1969-07-20

Initial stable release

### Changed

- Fully fueled lander to allow landing on the lunar surface
```