#!/bin/bash

# Set env vars and make available to child processes
export SYNC_SUBMODULES=true
export BUILD_TYPE=Incremental
export WORKSPACE=$PWD

# These are the args passed by main.yml, giving access to the dirs where master and gh-pages are checked out
ARGUMENT_LIST=(
  "master"
  "gh-pages"
)
# Read arguments using getopt (allows for long option, whereas getopts does not)
opts=$(getopt \
  --longoptions "$(printf "%s:," "${ARGUMENT_LIST[@]}")" \
  --name "$(basename "$0")" \
  --options "" \
  -- "$@"
)

eval set --$opts

while [[ $# -gt 0 ]]; do
  case "$1" in
    --master)
      masterArg=$2
      shift 2
      ;;

    --gh-pages)
      ghpagesArg=$2
      shift 2
      ;;

    *)
      break
      ;;
  esac
done

export MASTER=masterArg
export GH_PAGES=ghpagesArg

# Stop execution instantly as a query exits while having a non-zero status and xtrace
set -e -x

export ENABLED_THORNS="
  CactusElliptic/EllPETSc
  CactusUtils/TATPETSc
  ExternalLibraries/PETSc
"

if [ "$SYNC_SUBMODULES" = "true" ]; then
  git submodule sync
fi

# Creates the local configuration file for the submodules, if this configuration does not exist
git submodule update --init #--force
# Undo any local changes (do not use --force above since it always touches files)
git submodule foreach "git diff --quiet || git reset --hard"

if [ -r $WORKSPACE/configs/sim ]; then
  ( cd $WORKSPACE; make sim-cleandeps )
fi

# Need to force formattting of time so that we can parse it later
export LC_TIME=C

# Make files executable
chmod +x cactus/test-cactus
chmod +x cactus/build-cactus
# "time" outputs three times: real, user and sys
# "2>" redirects stderr to an (unspecified) file, "&1" redirects stderr to stdout.
# "tee" reads from the standard input and writes to (new) ./build.log file
# store.py copies this ./build.log file to {gh_pages}/records/version_{version}/build_{version}.log
time cactus/build-cactus $MASTER/manifest/einsteintoolkit.th 2>&1 | tee ./build.log
time cactus/test-cactus all