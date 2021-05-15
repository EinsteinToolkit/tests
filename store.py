'''
This file stores logs for future use in the records folder
'''
import shutil,os,glob

def copy_tests(test_dir,version,procs):
    '''
        This function copies individual test logs and diffs.
        It takes the directory of the logs, the version number 
        and then number of proceses.
    '''
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


def copy_logs(version):
    '''
        This copies the test logs for future use
    '''
    dst=f"./records/version_{version}/"
    builds=glob.glob("*.log")
    for build in builds:
        shutil.copy(build,dst+build.split(".")[0]+f"_{version}.log")


def copy_index(version):
    '''
        This copies the old html files showing test
        results for future use
    '''
    dst=f"./docs/index_{version}.html"
    index="./docs/index.html"
    if os.path.exists(index):
        shutil.copy(index,dst)
def copy_compile_log(version):
    '''
        This copies the compilation logs for future use
    '''
    dst=f"./records/version_{version}/build_{version}.log"
    build="./build.log"
    shutil.copy(build,dst)
def get_version():
    '''
        This checks the version of the current build
        by looking at the file names from old builds.
    '''
    current=0
    builds=glob.glob("./records/version_*")
    if(len(builds)!=0):
        builds=[int(x.split("_")[-1].split(".")[0]) for x in builds]
        current=max(builds)
    with open("./docs/version.txt",'w') as vers:
        for build_no in range(current,min(builds)-1,-1):
            if build_no==min(builds):
                vers.write(f"{build_no}")
            else:
                vers.write(f"{build_no}\n")
    return current+1

if __name__ == "__main__":
    dir1=os.path.expanduser("~/simulations/TestJob01_temp_1/output-0000/TEST/sim")
    dir2=os.path.expanduser("~/simulations/TestJob01_temp_2/output-0000/TEST/sim")
    version=get_version()
    os.mkdir(f"./records/version_{version}/")
    copy_logs(version)
    copy_tests(dir1,version,1)
    copy_tests(dir2,version,2)
