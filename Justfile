#!/usr/bin/env just --justfile

python := "python"

lint:
    {{ python }} -m flake8 yaclog/

format:
    {{ python }} -m black yaclog/
    {{ python }} -m yaclog format
    just --fmt --unstable

test *args:
    {{ python }} -m pytest {{ args }}

