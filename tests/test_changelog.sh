#!/bin/bash
echo TRAVIS_PULL_REQUEST_BRANCH=$TRAVIS_PULL_REQUEST_BRANCH
echo TRAVIS_PULL_REQUEST_BRANCH=$TRAVIS_PULL_REQUEST_BRANCH
echo TRAVIS_TAG=$TRAVIS_TAG
if [[ ( ! -z $TRAVIS_PULL_REQUEST_BRANCH ) && ( $TRAVIS_PULL_REQUEST_BRANCH != "develop" ) && ( -z $TRAVIS_TAG ) ]]; then
	[ ! -z "$(git diff develop... -- ../CHANGELOG.rst)" ] || ( echo "Remember to update the CHANGELOG.rst" && return 1 )
fi
