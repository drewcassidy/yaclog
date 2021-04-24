# Changelog

All notable changes to this project will be documented in this file

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