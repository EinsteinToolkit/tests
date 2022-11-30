#!/bin/bash

# TODO: pass $GITHUB_WORKSPACE/master to build-and-test.sh
echo "Master dir to refer to for testing: $1";
echo "Gh-pages dir to be passed to store.py: $2";

# Set env vars and make available to child processes
export SYNC_SUBMODULES=true
export CLEAN_CACTUS_JENKINS=true
export BUILD_TYPE=Incremental
export WORKSPACE=$PWD
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
rm -f build__*.log
# Work around bugs in Jenkins

if [ "$SYNC_SUBMODULES" = "true" ]; then
  git submodule sync
fi

# Creates the local configuration file for the submodules, if this configuration does not exist
git submodule update --init #--force
# Undo any local changes (do not use --force above since it always touches files)
git submodule foreach "git diff --quiet || git reset --hard"

# TODO: keep check?
# if [ "$CLEAN_CACTUS_JENKINS" = "true" -o ! -r $WORKSPACE/cactusjenkins ]; then
#   rm -rf $WORKSPACE/cactusjenkins
#   git clone https://bitbucket.org/ianhinder/cactusjenkins.git $WORKSPACE/cactusjenkins
# fi
if [ -r $WORKSPACE/configs/sim ]; then
  ( cd $WORKSPACE; make sim-cleandeps )
fi

# Need to force formattting of time so that we can parse it later
export LC_TIME=C

# TODO: pass MASTER and GH_PAGES to the referenced scripts (check final line in test-cactus)
# Make files executable
chmod +x test-cactus
chmod +x build-cactus
# "time" outputs three times: real, user and sys
# "tee" reads from the standard input and writes to ./build.log
time $WORKSPACE/build-cactus $MASTER/manifest/einsteintoolkit.th 2>&1 | tee ./build.log
time $WORKSPACE/test-cactus all
