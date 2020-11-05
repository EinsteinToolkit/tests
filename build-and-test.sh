#!/bin/bash
export SYNC_SUBMODULES=true
export CLEAN_CACTUS_JENKINS=true
export BUILD_TYPE=Incremental
cd einsteintoolkit
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
time $WORKSPACE/cactusjenkins/build-cactus manifest/einsteintoolkit.th > ./records/build.log
sed -i '2a export WORKSPACE=$PWD ' cactusjenkins/test-cactus
sed -i '2a export JOB_NAME="TestJob01" ' cactusjenkins/test-cactus
time $WORKSPACE/cactusjenkins/test-cactus all
python3 $WORKSPACE/logpage.py
# it takes ~1hr to build the docs
#time $WORKSPACE/cactusjenkins/build-cactus-doc

#cd $WORKSPACE/repos/carpet
#doxygen
