'''
Generates the HTML pages displaying various tables based on the logs.
'''

from collections import defaultdict
import re

import bokeh.models


def create_summary(file):
    '''
        This function parses the test results from the build__2_1.log file
        into a dictionary
    '''
    sum_data = {}
    with open(file, "r") as fp:
        lines = fp.read().splitlines()
        # Find the line where the summary starts
        i = 0
        while not re.match("^\s*Summary for configuration sim", lines[i]):
            i += 1
        i += 6
        # Loop until the end of the summary
        while not re.match("\s*Tests passed:", lines[i]):
            # The spacing of this line is unique and as such requires a special if statement
            if re.match("\s*Number passed only to\s*", lines[i]) and lines[i] != "":
                split_l = lines[i + 1].split("->")
                split_l[0] = lines[i] + " " + split_l[0]

                # Convert numerical data to integer
                try:
                    sum_data[" ".join(split_l[0].split())] = int(split_l[1].strip())
                except:
                    sum_data[" ".join(split_l[0].split())] = split_l[1]
                # This data field has to lines and as such increment the line counter twice
                i += 1

            # The regular line parsing code
            elif lines[i] != "":
                split_l = lines[i].split("->")
                try:
                    sum_data[" ".join(split_l[0].split())] = int(split_l[1].strip())
                except:
                    sum_data[" ".join(split_l[0].split())] = split_l[1]
            i += 1
    #print(sum_data)
    return sum_data


def get_tests(readfile):
    '''
        This functions reads the names of the tests that failed and passed
        from the log files and returns the set of them in tuples.
    '''
    passed = set()
    failed = set()
    with open(readfile, "r") as fp:
        lines = fp.read().splitlines()
        ind = 0
        while not re.match("\s*Tests passed:", lines[ind]):
            ind += 1
        ind += 2
        while not re.match("\s*Tests failed:", lines[ind]) and not re.match("=====*", lines[ind]):
            passed.add(" ".join(lines[ind].split()))
            ind += 1
        ind += 2
        while ind < len(lines) and not re.match("=====*", lines[ind]):
            failed.add(" ".join(lines[ind].split()))
            ind += 1
        if "" in passed:
            passed.remove("")
        if "" in failed:
            failed.remove("")
    return passed, failed


def test_comp(readfile_new, readfile_old):
    '''
        This function compares the tests from the previous run
        to see which failed, which failed this time but did
        not in the last, which passed this time but not in the last,
        and the new and removed tests.
    '''
    passed_n, failed_n = get_tests(readfile_new)
    passed_o, failed_o = get_tests(readfile_old)
    newly_p = passed_n - passed_o
    newly_f = failed_n - failed_o
    new_tests = (passed_n.union(failed_n)) - (passed_o.union(failed_o))
    missing_tests = (passed_o.union(failed_o)) - (passed_n.union(failed_n))
    types = ["Failed Tests", "Newly Passing Tests", "Newly Failing Tests", "Newly Added Tests", "Removed Tests"]
    tests = [failed_n, newly_p, newly_f, new_tests, missing_tests]
    test_dict = {types[i]: tests[i] for i in range(len(types))}
    return test_dict


def get_times(readfile):
    '''
        This function finds the times taken for each test in the log
        file and then stores that in a dictionary and then sorts
        those tests in descending order by time
    '''
    times = {}
    with open(readfile, "r") as fp:
        lines = fp.read().splitlines()
        ind = 0
        for line in lines:
            if re.match("\s*Details:", line):
                break
            ind += 1
        while ind < len(lines):
            try:
                time_i = lines[ind].index('(')
                tim = float(lines[ind][time_i + 1:].split()[0])
                test_name = lines[ind][:time_i - 1].split()[0]
                times[test_name] = tim
            except:
                pass
            ind += 1

    return {test: ti for test, ti in sorted(times.items(), key=lambda x: x[1],
                                            reverse=True)}  # This is a dictionary comprehension that uses sorted to order the items in times.items() into a dictionary


def exceed_thresh(time_dict, thresh):
    '''
        This function finds tests that exceed a certain time threshhold
    '''
    return {test: ti for test, ti in time_dict.items() if ti > thresh}


def longest_tests(time_dict, num_tests):
    '''
        This function finds the tests that took the longest time.
        It returns a dictionary of the num_test number of longest
        tests.
    '''
    longest = {}
    i = 0
    for item in time_dict.items():
        if i > num_tests - 1:
            break
        longest[item[0]] = item[1]
        i += 1
    return longest


def get_unrunnable(readfile):
    '''
        This test reads the logfile looking for tests that could not be run
        and the corresponding reason.
    '''
    miss_th = {}
    miss_proc = {}
    with open(readfile, "r") as fp:
        lines = fp.read().splitlines()
        ind = 0
        while not re.match("\s*Tests missed for lack of thorns:", lines[ind]):
            ind += 1
        ind += 2
        while not re.match("\s*Tests missed for different number of processors required:", lines[ind]):
            missing = lines[ind + 2].split(":")[1].split()
            miss_th[lines[ind].strip()] = missing
            ind += 4
        ind += 2
        while not re.match("\s*Tests with different number of test files:", lines[ind]):
            miss_proc[lines[ind].strip()] = lines[ind + 2].strip()
            ind += 4
    return miss_th, miss_proc


def get_data(name):
    '''
        Retrieves singular field of data from the data csv as a list
    '''
    data = {}
    with open('test_nums.csv', 'r') as csvfile:
        fields = csvfile.readline().strip().split(",")
        name_i = fields.index(name)
        line = csvfile.readline()
        while line != "":
            entry = line.strip().split(",")
            data[entry[0]] = float(entry[name_i])
            line = csvfile.readline()
    return data


def get_compile(name):
    '''
        Gets the total number of compile time warnings by using
        the get_warning_thorns function
    '''
    return sum(get_warning_thorns(name).values())


def get_warning_type(name):
    '''
        Compiles of counts of what types of warnings are produced the most
        during compilation
    '''
    warning_types = defaultdict(int)

    with open(name) as build:
        for line in build.readlines():
            m = re.search(".*/sim/build/([^/]*).* [wW]arning:", line)
            if (m):
                warning_types[line[line.find("[-W"):-1]] += 1
    return warning_types


def get_warning_thorns(name):
    '''
        This code finds how many compile time warnings are related each thorn
    '''
    warning_types = defaultdict(int)
    i = 0
    count = 0
    with open(name) as build:
        lines = build.readlines()
        for line in lines:
            i += 1
            # This regex search finds inline warnings based on the pattern given
            inline = re.search(".*/sim/build/([^/]*).* [wW]arning:", line)

            # This regex search finds the pattern shown below as twoline warnings are structure in this way
            twoline = re.search("[wW]arning:.*at", line)

            if (inline):
                trunc = line[line.find("build/") + 6:-1]
                trunc = trunc[:trunc.find("/")]
                warning_types[trunc] += 1
            if (twoline):
                count += 1
                nextl = lines[i + 1]
                nextnextl = lines[i + 2]
                warning = re.search(".*/sim/build/([^/]*).*", nextl)
                warning2 = re.search(".*/sim/build/([^/]*).*", nextnextl)
                if (warning):
                    trunc = nextl[nextl.find("build/") + 6:-1]
                    trunc = trunc[:trunc.find("/")]
                    warning_types[trunc] += 1
                if (warning2):
                    trunc = nextnextl[nextnextl.find("build/") + 6:-1]
                    trunc = trunc[:trunc.find("/")]
                    warning_types[trunc] += 1
    return warning_types


from requests.api import get
import sys
import os,csv,time,requests,math
from datetime import datetime
import matplotlib.pyplot as plt

# Different Bokeh modules
from bokeh.models.annotations import Legend
import bokeh.plotting as bplt
import bokeh.models.tools as btools
from bokeh.models import Panel, Tabs, DataRange1d
import bokeh.models.callbacks as bcall
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.layouts import row
from store import get_version,copy_index,get_commit_id
from bokeh.palettes import viridis
from bokeh.transform import factor_cmap
from bokeh.resources import CDN
from bokeh.embed import file_html

# to generate a commit log
from pygit2 import Repository, Oid
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE
from datetime import datetime, timezone, timedelta
import time

# Functions from parser.py
#from parser import create_summary, get_tests, get_warning_thorns, get_warning_type,test_comp,get_times,exceed_thresh,longest_tests,get_unrunnable,get_data,get_compile
import glob

records=os.listdir("./records")
curr_ver=get_version()-1
curr=f"./records/version_{curr_ver}/build__2_1_{curr_ver}.log"
last=f"./records/version_{curr_ver-1}/build__2_1_{curr_ver-1}.log"

repo = Repository('.git')
baseurl = repo.remotes["origin"].url.replace(":","/").replace("git@", "https://").replace(".git","")

def gen_commits():
    '''
        This function generates a list of commits that have been made since the last run
        If the workflow was run manually it will say so.
    '''

    # TODO: turn into convenience function
    curr_commit_id = Oid(hex=get_commit_id(curr_ver))
    last_commit_id = Oid(hex=get_commit_id(curr_ver-1))
    commits = []
    for commit in repo.walk(curr_commit_id, GIT_SORT_TOPOLOGICAL):
        if(commit.id == last_commit_id):
            break
        commits.append(commit)

    lines = []
    for count,commit in enumerate(commits):
        message=commit.message
        message=message.replace("\n\n","\n")
        message=message.replace('\n','<br>')
        #tzinfo = timezone(timedelta(minutes=commit.author.offset))
        #print(tzinfo)
        dt = datetime.fromtimestamp(commit.author.time, tz=timezone.utc)
        #print(dt)
        date = str(dt)
        lines.append("<tr> <td> <b> Commit: </b> </td> <td> <b> "+str(count+1)+" </b> </td> </tr> \n")
        lines.append("<tr> <td> Date: (In UTC)  </td> <td> "+date+"  </td> </tr> \n")
        lines.append("<tr> <td> Message: </td> <td>"+message+"</td> </tr> \n")
        #print(lines)
    return "\n".join(lines)

# log_link=f"{baseurl}/blob/master/records/version_{last_ver}/{last[ext-1:]+str(last_ver+1)}"
def gen_diffs(readfile):
    '''
        This function generates the html table that shows
        the comparison of test logs from last version generated
        by test_comp
    '''

    # The test_comp function provides tests that failed, were newly added or newly removed
    test_comparison=test_comp(readfile,last)
    if len(test_comparison["Failed Tests"])!=0:
        print("TESTS_FAILED=True")

    # Setup the header for the table
    output='''<table class="table table-bordered " >
    <caption style="text-align:center;font-weight: bold;caption-side:top">Failed Tests and Changes</caption>
    <tr><th></th><th>logs(1_process)</th><th>logs(2_processes)</th><th>diffs(1_process)</th><th>diffs(2_processes)</th></tr>\n'''

    for result in test_comparison.keys():
        # For each test make a header with the description of why that test is being shown(failed, newly added, newly failing)
        output+=f'''<tr><th colspan="5">'''+result+"</th></tr>\n"

        # If no such test exists add empty row
        if(len(test_comparison[result])==0):
            output+="<tr><td></td></tr>"

        # For each test get the thorn name and the current version
        for test in test_comparison[result]:
            thorn=test.split()[-1]
            thorn=thorn[:len(thorn)-1]
            test_name=test.split()[0]
            ver=curr_ver

            # Since the removed test would have been stored in the curr version subtract 1 from the version number
            if("Removed" in result):
                ver-=1

            # Links for logs and diffs of the tests in the test_comparison dictionary based on the number of procs
            logl1=f"{baseurl}/tree/gh-pages/records/version_{ver}/sim_{ver}_1/{thorn}/{test_name}.log"
            logl2=f"{baseurl}/tree/gh-pages/records/version_{ver}/sim_{ver}_2/{thorn}/{test_name}.log"
            diffl1=f"{baseurl}/tree/gh-pages/records/version_{ver}/sim_{ver}_1/{thorn}/{test_name}.diffs"
            diffl2=f"{baseurl}/tree/gh-pages/records/version_{ver}/sim_{ver}_2/{thorn}/{test_name}.diffs"

            # Check if these files are available if not display not avaible on the table 
            if(os.path.isfile("./"+logl1[logl1.find("records"):])):
                output+=f"  <tr><td>{test}</td><td><a href='{logl1}'>log</a></td>"
            else:
                output+=f" <tr><td>{test}</td><td>Not Available</td>"
            if(os.path.isfile("./"+logl2[logl2.find("records"):])):
                output+=f"  <td><a href='{logl2}'>log</a></td>"
            else:
                output+=f" <td>Not Available</td>"
            if(os.path.isfile("./"+diffl1[diffl1.find("records"):])):
                output+=f"<td><a href='{diffl1}'>diff</a></td>"
            else:
                output+=f"<td>Not Available</td>"  
            if(os.path.isfile("./"+diffl2[diffl2.find("records"):])):
                output+=f"<td><a href='{diffl2}'>diff</a></td></tr>\n"
            else:
                output+=f"<td>Not Available</td></tr>\n"  
    
    output+="</table>"
    return output


def gen_time(readfile):
    '''
        This function generates a table with the tests that took the longest time
    '''
    # The get_times function parses the data from the log files
    time_dict=get_times(readfile)

    # This part creates html table contianing the top 10 longest tests
    output='''<table class="table table-bordered " >
    <caption style="text-align:center;font-weight: bold;caption-side:top">Longest Tests</caption>\n'''
    output+="<tr><th>Test Name</th><th>Running Time</th>"
    for times in longest_tests(time_dict,10).keys():
        output+=f"   <tr><td>{times}</td><td>{time_dict[times]}s</td></tr>\n"
    output+="</table><br>"
    return output

def plot_test_data(readfile):

    # Get dataa from the csv and create lists for each field
    runnable=list(get_data("Runnable tests").values())
    times=list(get_data("Number of tests passed").keys())
    passed=list(get_data("Number of tests passed").values())
    time_taken=list(get_data("Time Taken").values())
    compile_warn=list((get_data("Compile Time Warnings").values()))
    build_no=list(get_data("Build Number").values())

    # Get the of dictionary of thorns with their warning counts
    warning_thorns=get_warning_thorns(f"records/version_{curr_ver}/build_{curr_ver}.log")

    # Turn that dictionary into lists so you can pick the thorns with most warnings
    counts=list(warning_thorns.values())
    counts_trunc=sorted(counts,reverse=True)[:7]
    warning_types_trunc=[]
    warning_types_list=list(warning_thorns.keys())

    for count in counts_trunc:
        i=counts.index(count)
        warning_types_trunc.append(warning_types_list[i])
        warning_types_list.pop(i)
        counts.pop(i)
    counts=counts_trunc
    warning_types_list=warning_types_trunc

    axis = [] # values displayed on the x axis

    Date = [] # dates in YYYY/MM/DD form
    for i in range(len(times)):
        date = datetime.fromtimestamp(float(float(times[i])), tz=None) # changing to UNIX timestamp from float
        axis.append(date)
        Date.append(date.strftime("%Y-%m-%d"))
        #print(axis)

    # The python library bokeh has a special data structure called a column data source that functions similarly
    # to a dictionary
    src=bplt.ColumnDataSource(data=dict(
        t=times,
        nt = axis,
        d = Date,
        b = build_no,
        rt=runnable,
        tp=passed,
        timet=time_taken,
        cmt=compile_warn,
        xax=[0]*len(times),
        url=[f"./index_{x+1}.html" for x in range(0,curr_ver)],
    ))

    # p is the first figure an area chart with the number of tests passed out of the ones ran
    # Tools attribute gives ways to manipulate the plot such as having clickable points, scrool to zoom and pan to zoom.
    # The rest of the attributes should be self explanatory
    # start = times[len(axis) - 10]
    # end = times[len(axis) - 1]
    # print(start, end)
    p=bplt.figure(x_range = (axis[len(axis) - 20], axis[len(axis) - 1]), y_range=(max(0, min(runnable)-30), max(runnable)+10), plot_width=1000, plot_height=600
                  ,tools="hover,tap,xwheel_zoom,box_zoom,reset",
           y_axis_label="Number of Tests", x_axis_label="Date", x_axis_type="datetime",
           title="Passed Tests", toolbar_location="below",sizing_mode='scale_width', tooltips=[("Date", "@d"),
            ("Runnable Tests", "@rt"), ("Passing Tests", "@tp"), ("Build", "@b")])
    # tooltips are used for the hover tool

    # Circles are points on the graph
    p.circle('nt', 'rt', size=10, color="green", source=src, legend_label="Runnable Tests")
    p.circle('nt', 'tp', size=10, color="blue", source=src, legend_label="Number of Tests Passed")

    # The taptool helps have these points link to the previous builds
    url = "@url"
    taptool = p.select(type=btools.TapTool)
    taptool.callback = bcall.OpenURL(url=url)

    # This part fills in the area below the points
    p.varea(y1='rt',y2='xax', x='nt', color="green",source=src,alpha=0.5)
    p.varea(y1='tp',y2='xax', x='nt', color="blue",source=src,alpha=0.5)

    

    # The graphs are displayed in a tabs and this part sets that up
    tab1 = Panel(child=p, title="Test Results")
    p.legend.location = "top_left"

    # This graph is for how long the testing part takes uses similar code to the first one but instead of area it has lines connecting points
    p1=bplt.figure(y_range=(0,max(time_taken)+5),plot_width=1000, plot_height=600,tools="tap,wheel_zoom,box_zoom,reset",
           y_axis_label="Time(minutes)", x_axis_label="Date", x_axis_type="datetime",
           title="Time Taken for Tests", toolbar_location="below",sizing_mode='scale_width')
    p1.circle('nt','timet',size=10,color="blue",source=src)
    p1.line('nt','timet',color="blue",source=src)
    taptool = p1.select(type=btools.TapTool)
    taptool.callback = bcall.OpenURL(url=url)
    tab2 = Panel(child=p1, title="Time Taken")


    # This graph is for the total number of compilation warnings and it uses the same code as the above plot but with different data
    p2=bplt.figure(y_range=(0,max(compile_warn)+50),plot_width=1000, plot_height=600,tools="tap,wheel_zoom,box_zoom,reset",
           title="Compilation Warnings",y_axis_label="Number of Compilation Warnings", x_axis_label="Date", x_axis_type="datetime",
           toolbar_location="below",sizing_mode='scale_width')
    p2.circle('nt','cmt',size=10,color="blue",source=src)
    p2.line('nt','cmt',color="blue",source=src)
    taptool = p2.select(type=btools.TapTool)
    taptool.callback = bcall.OpenURL(url=url)
    tab3 = Panel(child=p2, title="Compile Time Warnings")

    src1=bplt.ColumnDataSource(data=dict(cts=counts,
        wts=warning_types_list))

    # This plot is a bar graph showing the top 7 thorns with the most warnings
    p3=bplt.figure(x_range=warning_types_list,plot_width=1200, title="Compilation Warning Thorns",
           y_axis_label="Number of Warnings", x_axis_label="Name of Thorn",
           toolbar_location="below", tools="tap,wheel_zoom,box_zoom,reset",sizing_mode='scale_width')
    p3.vbar(x='wts', top='cts', width=0.9, source=src1,
       line_color='white', fill_color=factor_cmap('wts', palette=viridis(len(counts)), factors=warning_types_list))
    tab4=Panel(child=p3, title="Compilation Warning Thorns")

    p.xaxis.major_label_orientation = math.pi/6
    p1.xaxis.major_label_orientation = math.pi/6
    p2.xaxis.major_label_orientation = math.pi/6


    # Bokeh createst the html script and javscript for the plots using this code
    html = file_html(Tabs(tabs=[tab1, tab2,tab3]), CDN, "Plots")
    with open("./docs/plot.html","w") as fp:
        fp.write(html)
    #script, div = components(Tabs(tabs=[tab1, tab2,tab3]))
    script, div=components(p3)
    return script,div


def gen_unrunnable(readfile):
    '''
        This function generates a html showing which tests could not be run and the reason
    '''
    m,n=get_unrunnable(readfile)
    output=''' <table class="table table-bordered " >
    <caption style="text-align:center;font-weight: bold;caption-side:top">Unrunnable Tests</caption>\n'''
    output+="<tr><th>Tests Missed for Lack Of Thorns</th><th>Missing Thorns</th></tr>\n"
    for test in m.keys():
        thorns=','.join(m[test])
        output+=f"  <tr><td>{test}</td><td>{thorns}</td></tr>\n"
    output+="<tr><th>Tests missed for different number of processors required:</th><th>Processors Required</th></tr>\n"
    for test in n.keys():
        output+=f"  <tr><td>{test}</td><td>{n[test]}</td></tr>\n"
    output+="</table>"
    return output

def summary_to_html(readfile,writefile):
    '''
        This function reads the log file and outputs and html
        page with the summary in a table
    '''

    data=create_summary(readfile)
    
    contents=""
    script,div=plot_test_data(readfile)


    # Check Status Using the data from the summary
    status="All Tests Passed"
    if data["Number of tests passed"]==0:
        status="All Tests Passed"
    elif data["Number failed"]!=0:
        status="Some Tests Failed"
        # Send email if tests failed
        #os.system(f'python3 mail.py')
    with open(writefile,"w") as fp:
        for key in data.keys():

            # Add a table row for each data field
            contents+=f"        <tr><th>{key}</th><td>{data[key]}</td><tr>\n"

        # The formatted string holds the html template and loads in the values for content and status    
        template=f'''<!doctype html>
    <html lang="en">
        <head>
            <title>Summary of Tests</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
            <style>
            .bk-root .bk {{
                margin: 0 auto !important;
            }}
            </style>
            <style>
            .sidebar {{
                height: 100%; 
                width: 150px;
                position: fixed;
                z-index: 1; 
                top: 0; 
                left: 0;
                background-color: #212529; 
                overflow-x: hidden;
                padding-top: 20px; 
            }}
            .sidebar a {{
                padding: 6px 8px 6px 16px;
                text-decoration: none;
                font-size: 18px;
                color: #dbdcdd;
                display: block;
                }}
            .sidebar a:hover {{
                color: white;
            }}
            .container{{
              padding-left: 150px;
              font-size: 18px;
            }}
                        /* On screens that are less than 700px wide, make the sidebar into a topbar */
            @media screen and (max-width: 500px) {{
            .sidebar {{
              display: none;
            }}
            .container {{
              padding-left:0px;
            }}
            }}
            </style>
            <script src="https://cdn.bokeh.org/bokeh/release/bokeh-2.0.1.min.js"
            crossorigin="anonymous"></script>
            {script}

        </head>
        <body>
            <div class="sidebar">
            </div>
            <script src='version.js'>
            </script>
            <div class="container">
                <h1 style="text-align:center">{status}</h1>
                <h3 style="text-align:center"><a href="{baseurl}/tree/gh-pages/records/version_{curr_ver}">Build #{curr_ver}</a></h3>
                <table class="table table-bordered " >
                <caption style="text-align:center;font-weight: bold;caption-side:top">Summary</caption>
                {contents}
                </table>
                <br>
                <table class="table table-bordered " >
                <caption style="text-align:center;font-weight: bold;caption-side:top">Commits in Last Push</caption>
                {gen_commits()}
                </table>
                {gen_diffs(readfile)}
                <br>
                {gen_time(readfile)}
                <br>
                {gen_unrunnable(readfile)}
                <br>
                <table style="margin: 0 auto;">
                    <iframe src="plot.html" height="700" width="1100"></iframe>
                </table>
                <table style="margin: 0 auto;">
                    {div}
                </table>
            <div>
            
        </body>
    </html>
        '''
        fp.write(template)

def write_to_csv(readfile):
    '''
        This function is used to store data between builds into a csv
    '''

    total=sum(x[1] for x in get_times(readfile).items()) #

    data=create_summary(readfile)
    data["Time Taken"]=total/60
    local_time = str(int(time.time()))  #datetime.today().strftime('%s') to convert to unix timestamp instead of a
    # normal date format. This helps in plotting as all x axis elements are now unique
    #local_time+=f"({curr_ver})"
    data["Compile Time Warnings"]=get_compile(f"records/version_{curr_ver}/build_{curr_ver}.log")
    with open('test_nums.csv','a') as csvfile:
        contents=f"{local_time}"
        for key in data.keys():
            contents+=f",{data[key]}"
        contents += f",{curr_ver}"
        contents+="\n"
        csvfile.write(contents)
#import glob, glob.glob("records/*/"build_1_2_*")



if __name__ == "__main__":
    write_to_csv(curr)
    summary_to_html(curr,"docs/index.html")
    copy_index(get_version()-1)
    test_comparison=test_comp(curr,last)
    if len(test_comparison["Failed Tests"])!=0 or len(test_comparison["Newly Passing Tests"])!=0 :
        os.system("python3 mail.py")


