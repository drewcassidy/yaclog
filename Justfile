#!/usr/bin/env just --justfile

# Actions relating to documentation
mod docs

source_dirs := "yaclog/ tests/"

# Lint python source code
lint:
    pyflakes {{ source_dirs }}
    black --check {{ source_dirs }}
    zuban check {{ source_dirs }}

# Format python source code and other support files
format: && docs::format
    black {{ source_dirs }}
    mdformat README.md
    yaclog format
    '{{ just_executable() }}' --fmt --unstable

# Run tests
test *args:
    pytest {{ args }}

# Build distribution
build:
    pipx run build

pre-commit := f"""
  #!/bin/sh
  PATH={{ `dirname "$(which python)"` }}:$PATH just lint test"""

# Install recommended git hooks. Do this after activating your virtual environment
install-hooks:
    echo '{{ pre-commit }}' > .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
