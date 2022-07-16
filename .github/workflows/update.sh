#!/bin/bash

set -e -x

git submodule init
awk '/^[[]submodule "/{print "update = !git reset --quiet --mixed"} {print}' .git/config >.git/config.tmp
mv .git/config.tmp .git/config
# --init required to due Kranc containing another submodule
git submodule update --init --recursive --remote --no-fetch --depth 1 --jobs 4
git add --all

# need commits to produce list of changes
# unfortunately git fetch --shallow-exclude=refspec does not work and fails
# with an error message
for m in $(git diff --cached --name-only) ; do  (
  cd $m
  git fetch --unshallow
) done

if ! git diff --cached --exit-code --quiet ; then
  git config --global user.email "maintainters@einsteintoolkit.org"
  git config --global user.name "GitHub updater"
  git commit -q -F - <<EOF
updated submodules

$(git diff --cached --submodule=log)
EOF
  # could use GITHUB_SERVER_URL but it requires inserting
  # text after the https:// in it which is annoying
  git remote set-url --push origin "https://x-access-token:${PERSONAL_TOKEN}@github.com/${GITHUB_REPOSITORY}"
  git push
fi
