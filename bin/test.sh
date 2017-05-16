#!/bin/sh

set -e

py.test tests -v

flake8 rlselect rlselectlib tests

echo PASS
