#!/bin/sh

set -e

py.test tests -v

flake8 selectlib

echo PASS
