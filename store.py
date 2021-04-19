import shutil,os,glob

def copy_tests(test_dir,version,procs):
    dst=f"./records/version_{version}/sim_{version}_{procs}"
    dirlist=os.listdir(test_dir)
    if not os.path.isdir(dst):
        os.mkdir(dst)
    for dir in dirlist:
        if(not os.path.isdir(dst+"/"+dir)):
            os.mkdir(dst+"/"+dir)
        diffs=[x.split("/")[-1] for x in glob.glob(test_dir+"/"+dir+"/*.diffs")]
        logs=[x.split("/")[-1] for x in glob.glob(test_dir+"/"+dir+"/*.log")]
        for log in logs:
            shutil.copy(test_dir+"/"+dir+"/"+log,dst+"/"+dir+"/"+log)
        for diff in diffs:
            shutil.copy(test_dir+"/"+dir+"/"+diff,dst+"/"+dir+"/"+diff)

    #shutil.copytree(test_dir,dst,)


def copy_builds(version):
    
    dst=f"./records/version_{version}/"
    builds=glob.glob("*.log")
    for build in builds:
        shutil.copy(build,dst+build.split(".")[0]+f"_{version}.log")


def copy_index(version):
    dst=f"./docs/index_{version}.html"
    index="./docs/index.html"
    if os.path.exists(index):
        shutil.copy(index,dst)
def copy_build_log(version):
    dst=f"./records/version_{version}/build_{version}.log"
    build="./build.log"
    shutil.copy(build,dst)
def get_version():
    current=0
    builds=glob.glob("./records/version_*")
    if(len(builds)!=0):
        builds=[int(x.split("_")[-1].split(".")[0]) for x in builds]
        current=max(builds)
    with open("./docs/version.txt",'w') as vers:
        vers.write(f"{current+1}")
    return current+1

if __name__ == "__main__":
    dir1=os.path.expanduser("~/simulations/TestJob01_temp_1/output-0000/TEST/sim")
    dir2=os.path.expanduser("~/simulations/TestJob01_temp_2/output-0000/TEST/sim")
    version=get_version()
    os.mkdir(f"./records/version_{version}/")
    copy_builds(version)
    copy_tests(dir1,version,1)
    copy_tests(dir2,version,2)