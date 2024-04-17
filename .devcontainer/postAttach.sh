#!/usr/bin/env bash
set -eu

git config --global --add safe.directory /home/calitp/app
pre-commit install --install-hooks
