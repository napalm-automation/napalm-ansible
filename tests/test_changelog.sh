#!/bin/sh
[ ! -z "$(git diff develop... -- ../CHANGELOG.rst)" ] || ( echo "Remember to update the CHANGELOG.rst" && return 1 )
