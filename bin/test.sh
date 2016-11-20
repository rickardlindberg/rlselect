#!/bin/sh

set -e

py.test tests -v

flake8 select selectlib tests

echo PASS
