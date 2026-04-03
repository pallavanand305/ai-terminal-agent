#!/usr/bin/env bash
# Do not modify this file.
set -e
pip install --quiet requests==2.31.0 pytest==7.4.3
pytest /tests/test_outputs.py -v
