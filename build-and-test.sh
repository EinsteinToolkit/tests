#!/bin/bash

# TODO: pass $GITHUB_WORKSPACE/master to build-and-test.sh
echo "Master dir to refer to for testing: $1";
echo "Gh-pages dir to be passed to store.py: $2";

# Set env vars and make available to child processes
export SYNC_SUBMODULES=true
export CLEAN_CACTUS_JENKINS=true
export BUILD_TYPE=Incremental
# TODO: debug: in GitHub this is $GITHUB_WORKSPACE/scripts
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

# TODO: remove this? Or access via gh-pages
rm -f build__*.log
# Work around bugs in Jenkins

if [ "$SYNC_SUBMODULES" = "true" ]; then
  git submodule sync
fi

# Creates the local configuration file for the submodules, if this configuration does not exist
git submodule update --init #--force
# Undo any local changes (do not use --force above since it always touches files)
git submodule foreach "git diff --quiet || git reset --hard"

# TODO: remove external dependency, access locally
# if [ "$CLEAN_CACTUS_JENKINS" = "true" -o ! -r $WORKSPACE/cactusjenkins ]; then
#   rm -rf $WORKSPACE/cactusjenkins
#   git clone https://bitbucket.org/ianhinder/cactusjenkins.git $WORKSPACE/cactusjenkins
# fi
if [ -r $WORKSPACE/configs/sim ]; then
  ( cd $WORKSPACE; make sim-cleandeps )
fi

# Need to force formattting of time so that we can parse it later
export LC_TIME=C

# TODO: make changes to local files, no sed
# TODO: pass MASTER and GH_PAGES to the referenced scripts
# This outputs three times: real, user and sys
time $WORKSPACE/build-cactus $MASTER/manifest/einsteintoolkit.th 2>&1 | tee ./build.log
sed -i '2a export WORKSPACE=$PWD ' test-cactus
sed -i '2a export JOB_NAME="TestJob01" ' test-cactus
sed -i '2a set -x ' test-cactus
sed -i '/rm -rf \$simdir\/\$simname/d' test-cactus
sed -i '43a rm -rf \$simdir\/\$simname' test-cactus
# TODO: check if gh-pages is properly passed
sed -i -e '$a python3 store.py . $GH_PAGES $HOME/simulations/TestJob01_temp_1/output-0000/TEST/sim $HOME/simulations/TestJob01_temp_2/output-0000/TEST/sim || true' test-cactus
time $WORKSPACE/test-cactus all
