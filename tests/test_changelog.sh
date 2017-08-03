#!/bin/bash
echo TRAVIS_PULL_REQUEST_BRANCH=$TRAVIS_PULL_REQUEST_BRANCH
echo TRAVIS_TAG=$TRAVIS_TAG
if [[ ( ! -z $TRAVIS_PULL_REQUEST_BRANCH ) && ( $TRAVIS_PULL_REQUEST_BRANCH != "develop" ) && ( -z $TRAVIS_TAG ) ]]; then
	echo "Checking for CHANGELOG changes"
	[ ! -z "$(git diff develop... -- ../CHANGELOG.rst)" ] || ( echo "Remember to update the CHANGELOG.rst" && exit 1 )
else
	echo "Not checking for CHANGELOG changes"
fi
