#!/bin/bash
# TODO: remove debug prints
echo "Master dir to refer to for testing: $1";
echo "Gh-pages dir to be passed to store.py: $2";

# Set env vars and make available to child processes
export SYNC_SUBMODULES=true
export BUILD_TYPE=Incremental
export WORKSPACE=$PWD
# These are the args passed by main.yml, giving access to the dirs where master and gh-pages are checked out
export MASTER=$1
export GH_PAGES=$2

# Stop execution instantly as a query exits while having a non-zero status and xtrace
set -e -x

export ENABLED_THORNS="
  CactusElliptic/EllPETSc
  CactusUtils/TATPETSc
  ExternalLibraries/PETSc
"

# TODO: remove this? Or access via GH_PAGES?
# rm -f build__*.log
# Work around bugs in Jenkins

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
time cactus/build-cactus $MASTER/manifest/einsteintoolkit.th 2>&1 | tee ./build.log
time cactus/test-cactus all
