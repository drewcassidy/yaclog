#!/usr/bin/env just --justfile

# Actions relating to documentation
mod docs

python := "python"

# Lint python source code
lint:
    {{ python }} -m flake8 yaclog/

# Format python source code and other support files
format: && docs::format
    {{ python }} -m black yaclog/
    {{ python }} -m yaclog format
    just --fmt --unstable

# Run tests
[arg("args", help="Arguments passed to pytest")]
test *args:
    {{ python }} -m pytest {{ args }}
