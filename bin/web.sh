#!/usr/bin/env bash
set -eu

python -m http.server -d ./tests/coverage
