#!/bin/bash
export SYNC_SUBMODULES=true
export CLEAN_CACTUS_JENKINS=true
export BUILD_TYPE=Incremental
export WORKSPACE=$PWD
set -e -x

export ENABLED_THORNS="
  CactusElliptic/EllPETSc
  CactusUtils/TATPETSc
  ExternalLibraries/PETSc
"

rm -f build__*.log
# Work around bugs in Jenkins

if [ "$SYNC_SUBMODULES" = "true" ]; then
  git submodule sync
fi

git submodule update --init #--force
# undo any local changes (do not use --force above since it always touches
# files)
git submodule foreach "git diff --quiet || git reset --hard"

if [ "$CLEAN_CACTUS_JENKINS" = "true" -o ! -r $WORKSPACE/cactusjenkins ]; then
  rm -rf $WORKSPACE/cactusjenkins
  git clone https://bitbucket.org/ianhinder/cactusjenkins.git $WORKSPACE/cactusjenkins
fi
if [ -r $WORKSPACE/configs/sim ]; then
  ( cd $WORKSPACE; make sim-cleandeps )
fi

# need to force formattting of time so that we can parse it later
export LC_TIME=C

time $WORKSPACE/cactusjenkins/build-cactus manifest/einsteintoolkit.th 2>&1 | tee ./build.log
sed -i '2a export WORKSPACE=$PWD ' cactusjenkins/test-cactus
sed -i '2a export JOB_NAME="TestJob01" ' cactusjenkins/test-cactus
sed -i '2a set -x ' cactusjenkins/test-cactus
sed -i '/rm -rf \$simdir\/\$simname/d' cactusjenkins/test-cactus
sed -i '43a rm -rf \$simdir\/\$simname' cactusjenkins/test-cactus
# First arg $1 is path to $GITHUB_WORKSPACE/gh-pages, passed by CI
sed -i -e '$a python3 store.py . $HOME/simulations/TestJob01_temp_1/output-0000/TEST/sim $HOME/simulations/TestJob01_temp_2/output-0000/TEST/sim $1 || true' cactusjenkins/test-cactus
time $WORKSPACE/cactusjenkins/test-cactus all
