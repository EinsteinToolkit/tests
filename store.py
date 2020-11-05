import shutil,os,glob

def copy_tests(test_dir,version):
    dst=f"./records/sim_{version}"
    dirlist=os.listdir(test_dir)
    os.mkdir(dst)
    for dir in dirlist:
        if(os.path.isdir(test_dir+"/"+dir)):
            os.mkdir(dst+"/"+dir)
            diffs=[x.split("/")[-1] for x in glob.glob(test_dir+"/"+dir+"/*.diffs")]
            logs=[x.split("/")[-1] for x in glob.glob(test_dir+"/"+dir+"/*.log")]
            for log in logs:
                shutil.copy(test_dir+"/"+dir+"/"+log,dst+"/"+dir+"/"+log)
            for diff in diffs:
                shutil.copy(test_dir+"/"+dir+"/"+diff,dst+"/"+dir+"/"+diff)

    #shutil.copytree(test_dir,dst,)


def copy_builds(version):
    dst="./records/"
    builds=glob.glob("*.log")
    for build in builds:
        shutil.copy(build,dst+build.split(".")[0]+f"_{version}.log")


def copy_index(version):
    dst=f"./docs/index_{version}.html"
    index="./docs/index.html"
    shutil.copy(index,dst)
def copy_build_log(version):
    dst=f"./records/build_{version}.log"
    build="./records/build.log"
    shutil.copy(build,dst)
def get_version():
    builds=glob.glob("./records/*.log")
    current=0
    if(len(builds)!=0):
        current=int(builds[-1].split("_")[-1].split(".")[0])
    return current+1

if __name__ == "__main__":
    dir=os.path.expanduser("~/simulations/TestJob01_temp_2/output-0000/TEST/sim")
    version=get_version()
    copy_builds(version)
    copy_index(version)
    copy_tests(dir,version)