#!/bin/sh

set -e

py.test test_rlselect.py -v

echo PASS
