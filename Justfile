#!/usr/bin/env just --justfile

mod docs

python := "python"

lint:
    {{ python }} -m flake8 yaclog/

format:
    {{ python }} -m black yaclog/
    {{ python }} -m yaclog format
    just --fmt --unstable
    cd docs && just --fmt --unstable

test *args:
    {{ python }} -m pytest {{ args }}
