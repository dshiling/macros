#!/bin/sh
set -e

echo "Checking style and conventions..."
pylint --persistent=n macros migrations tests

echo "Starting tests..."
py.test -p no:cacheprovider
