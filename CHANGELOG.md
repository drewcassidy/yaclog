# Changelog

All notable changes to this project will be documented in this file

## 0.3.3 - 2021-04-27

### Added

- Unit tests in the `tests` folder

### Changed

- Default links and dates in VersionEntry are now consistently `None`
- Changelog links dict now contains version links. 
  Modified version links will overwrite those in the table when writing to a file
- Changelog object no longer errors when creating without a path.
- `release` now resets lesser version values when incrementing
- `release` now works with logs that have only unreleased changes

## 0.3.2 - 2021-04-24

### Added

- Readme file now has installation and usage instructions.
- yaclog command entry point added to setup.cfg.

### Changed

- `release -c` will no longer create empty commits, and will use the current commit instead.

### Fixed

- `release` and `entry` commands now work using empty changelogs.

## 0.3.1 - 2021-04-24

### Added

- `yaclog` tool for manipulating changelogs from the command line
    - `init` command to make a new changelog
    - `format` command to reformat the changelog
    - `show` command to show changes from the changelog
    - `entry` command for manipulating entries in the changelog
    - `tag` command for manipulating tags in the changelog
    - `release` command for creating releases

## 0.2.0 - 2021-04-19

### Added

- New yak log logo drawn by my sister

### Changed

- Updated package metadata
- Rewrote parser to use a 2-step method that is more flexible.
    - Parser can now handle code blocks.
    - Parser can now handle setext-style headers and H2s not conforming to the schema.

## 0.1.0 - 2021-04-16

First release

### Added

- `yaclog.read()` method to parse changelog files