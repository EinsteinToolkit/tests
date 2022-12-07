from requests.api import get
import sys
import os,csv,time,requests,math
from datetime import datetime
import matplotlib.pyplot as plt
import shutil

# Different Bokeh modules
from bokeh.models.annotations import Legend
import bokeh.plotting as bplt
import bokeh.models.tools as btools
from bokeh.models import Panel, Tabs, DataRange1d
import bokeh.models.callbacks as bcall
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.layouts import row
from store import get_version,copy_build,get_commit_id
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
from parser import create_summary, get_tests, get_warning_thorns, get_warning_type,test_comp,get_times,exceed_thresh,\
    longest_tests,get_unrunnable,get_data,get_compile
import glob

master = sys.argv[1]
gh_pages = sys.argv[2] 
repo = Repository(f"{master}/.git") 
baseurl = repo.remotes["origin"].url.replace("git@", "https://").replace(".git","")

records=os.listdir(f"{gh_pages}/records")
# curr_ver=get_version()
# curr=f"{gh_pages}/records/version_{curr_ver}/build__2_1_{curr_ver}.log"
# last=f"{gh_pages}/records/version_{curr_ver-1}/build__2_1_{curr_ver-1}.log"
curr_ver=-1
curr = None
last = None

def set_curr_version(count):
    '''
        This function updates the global variables on every iteration 
        (see the loop in main below)
    '''
    global curr_ver
    global curr
    global last
    curr_ver = count
    curr=f"{gh_pages}/records/version_{curr_ver}/build__2_1_{curr_ver}.log"
    last=f"{gh_pages}/records/version_{curr_ver-1}/build__2_1_{curr_ver-1}.log"
    return curr_ver

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
        tzinfo = timezone(timedelta(minutes=commit.author.offset))
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
    # if len(test_comparison["Failed Tests"])!=0:
    #     print("TESTS_FAILED=True", file=open(os.environ["GITHUB_ENV"], "a"))

    # Setup the header for the table
    output='''<table class="table table-bordered " >
    <caption style="text-align:center;font-weight: bold;caption-side:top">Failed Tests and Changes</caption>
    <tr><th></th><th>logs(1_process)</th><th>logs(2_processes)</th><th>diffs(1_process)</th><th>diffs(2_processes)</th><th>first failure</th></tr>\n'''

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
                output+=f"  <tr><td>{test}</td><td><a href='{logl1}' target='_blank'>log</a></td>"
            else:
                output+=f" <tr><td>{test}</td><td>Not Available</td>"
            if(os.path.isfile("./"+logl2[logl2.find("records"):])):
                output+=f"  <td><a href='{logl2}' target='_blank'>log</a></td>"
            else:
                output+=f" <td>Not Available</td>"
            if(os.path.isfile("./"+diffl1[diffl1.find("records"):])):
                output+=f"<td><a href='{diffl1}' target='_blank'>diff</a></td>"
            else:
                output+=f"<td>Not Available</td>"  
            if(os.path.isfile("./"+diffl2[diffl2.find("records"):])):
                output+=f"<td><a href='{diffl2}' target='_blank'>diff</a></td>\n"
            else:
                output+=f"<td>Not Available</td>\n"  

            # If this test instance was a failed test, find the first time it failed
            if(result == 'Failed Tests'):
                first_failure =  get_first_failure(test)
                # No report found with first failure
                if (first_failure) == -1:
                    output+=f"<td>Not Available</td>\n"  
                else :
                    first_failure_link=f'build_{first_failure}.html'
                    output+=f"<td><a href='{first_failure_link}' target='_blank'>report</a></td></tr>\n"
    
    output+="</table>"
    return output

def get_first_failure(test_name):
    '''
        This function returns the number of the first version when this test failed
    '''
    # Dummy value which will be returned if none found
    first_failure = -1

    for i in range(curr_ver, 1, -1):
        log_to_check=f"{gh_pages}/records/version_{i}/build__2_1_{i}.log"
        prev_log_to_check=f"{gh_pages}/records/version_{i-1}/build__2_1_{i-1}.log"
        # Dictionary containing keys: "Failed Tests","Newly Passing Tests","Newly Failing Tests","Newly Added Tests", "Removed Tests"
        curr_res = test_comp(log_to_check, prev_log_to_check)
        if (test_name in curr_res["Newly Failing Tests"]):
            first_failure = i
            break
        # If i = 2 and test is not found under "Newly failing tests", then it must have failed for the first time in report 1
        elif (i == 2):
            first_failure = 1

    return first_failure
    

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
    warning_thorns=get_warning_thorns(f"{gh_pages}/records/version_{curr_ver}/build_{curr_ver}.log")

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
    # TODO: check if the url is correct
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
        url=[f"./build_{x+1}.html" for x in range(0,curr_ver)],
    ))

    # p is the first figure an area chart with the number of tests passed out of the ones ran
    # Tools attribute gives ways to manipulate the plot such as having clickable points, scrool to zoom and pan to zoom.
    # The rest of the attributes should be self explanatory
    # start = times[len(axis) - 10]
    # end = times[len(axis) - 1]
    # print(start, end)
    p=bplt.figure(x_range = (axis[max(0, len(axis) - 20)], axis[-1]), y_range=(max(0, min(runnable)-30), max(runnable)+10), plot_width=1000, plot_height=600
                  ,tools="hover,tap,pan,xwheel_zoom,box_zoom,reset"
                  ,active_scroll="xwheel_zoom",
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
    p1=bplt.figure(y_range=(0,max(time_taken)+5),plot_width=1000, plot_height=600,tools="tap,pan,wheel_zoom,box_zoom,reset",
           active_scroll="wheel_zoom",
           y_axis_label="Time(minutes)", x_axis_label="Date", x_axis_type="datetime",
           title="Time Taken for Tests", toolbar_location="below",sizing_mode='scale_width')
    p1.circle('nt','timet',size=10,color="blue",source=src)
    p1.line('nt','timet',color="blue",source=src)
    taptool = p1.select(type=btools.TapTool)
    taptool.callback = bcall.OpenURL(url=url)
    tab2 = Panel(child=p1, title="Time Taken")


    # This graph is for the total number of compilation warnings and it uses the same code as the above plot but with different data
    p2=bplt.figure(y_range=(0,max(compile_warn)+50),plot_width=1000, plot_height=600,tools="tap,pan,wheel_zoom,box_zoom,reset",
           active_scroll="wheel_zoom",
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
           toolbar_location="below", tools="tap,pan,wheel_zoom,box_zoom,reset",
           active_scroll="wheel_zoom", sizing_mode='scale_width')
    p3.vbar(x='wts', top='cts', width=0.9, source=src1,
       line_color='white', fill_color=factor_cmap('wts', palette=viridis(len(counts)), factors=warning_types_list))
    tab4=Panel(child=p3, title="Compilation Warning Thorns")

    p.xaxis.major_label_orientation = math.pi/6
    p1.xaxis.major_label_orientation = math.pi/6
    p2.xaxis.major_label_orientation = math.pi/6


    # Bokeh createst the html script and javscript for the plots using this code
    html = file_html(Tabs(tabs=[tab1, tab2,tab3]), CDN, "Plots")
    with open(f"{gh_pages}/docs/plot.html","w") as fp:
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
        thorns=', '.join(m[test])
        output+=f"  <tr><td>{test}</td><td>{thorns}</td></tr>\n"
    output+="<tr><th>Tests missed for different number of processors required:</th><th>Processors Required</th></tr>\n"
    for test in n.keys():
        output+=f"  <tr><td>{test}</td><td>{n[test]}</td></tr>\n"
    output+="</table>"
    return output

def create_sidebar():
    '''
        Creates sidebar.html containing all build numbers 
        that gets injected into the HTML page created in summary_to_html
    '''
    # Add GitHub badge on top of sidebar, will be injected by version.js
    template =f'''
        <div class="workflow-status"> </div>
    '''

    # For every version, create link and symbol in sidebar
    for i in range(get_version(), 0, -1):
        # The build file will be displayed in new tab
        template +='<a href="build_' + str(i) + '.html" target="results_iframe"> Build #' + str(i) + '</a>'
        # Check whether the build passed or not by calling parser
        log_to_check=f"{gh_pages}/records/version_{i}/build__2_1_{i}.log"
        # Get failed tests only from returned tuple
        curr_res = get_tests(log_to_check)[1]
        if len(curr_res) != 0:
            template += '<img src="exclamation.svg" style="display: inline; width: 30px; height: 30px; float: right; margin-right: 14px;">'
        else:
            template += '<img src="check.svg" style="display: inline; width: 30px; height: 30px; float: right; margin-right: 14px;">'

    return template

def create_test_results(readfile):
    '''
        Creates test results for the given log file,
        which gets displayed to the right of the sidebar
    '''

    data=create_summary(readfile)
    script, div=plot_test_data(readfile)

    # Check Status Using the data from the summary
    status="All Tests Passed"
    if data["Number failed"]!=0:
        status="Some Tests Failed"
        # Send email if tests failed
        #os.system(f'python3 mail.py')
    dateFormatter = "%a %b %d %H:%M:%S %Z %Y"
    build_dt = datetime.strptime(data["Time"], dateFormatter)
    build_dt_utc = build_dt.replace(tzinfo=timezone.utc)  # changing to UTC
    build_date = build_dt_utc.strftime(dateFormatter)

    summary_contents=""
    for key in ["Total available tests", "Unrunnable tests", "Runnable tests", "Total number of thorns", "Number of tested thorns", "Number of tests passed", "Number passed only to set tolerance", "Number failed"]:
        # Add a table row for each data field
        summary_contents+=f"<tr><th>{key}</th><td>{data[key]}</td><tr>\n"

    template= f'''
                <!doctype html>
                <html lang="en">
                <head>
                    <title>Results of Tests</title>
                    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
                    <style>
                    .bk-root .bk {{
                        margin: 0 auto !important;
                    }}
                    html {{
                        padding-left: 150px; 
                        padding-right: 150px;
                    }}
                    </style>
                    <script src="https://cdn.bokeh.org/bokeh/release/bokeh-2.0.1.min.js"
                    crossorigin="anonymous"></script>
                    {script}
                </head>
                <body>
                    <h1 style="text-align:center">{status}</h1>
                    <h3 style="text-align:center">
                        <a href="{baseurl}/tree/gh-pages/records/version_{curr_ver}" target="_blank">Build #{curr_ver}</a>
                    </h3>
                    <h6 style="text-align:center">
                        <a href="index.html" target="_blank">Go to latest build</a>
                    </h6>
                    <h3 style="text-align:center">{build_date}</h3>
                    <table class="table table-bordered " >
                    <caption style="text-align:center;font-weight: bold;caption-side:top">Summary</caption>
                    {summary_contents}
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
                        <!-- height determined by height of plots inside (600ox) -->
                        <iframe src="plot.html" style="height: 700px; width: 100%"></iframe>
                    </table>
                    <div style="margin: 0 auto;">
                        {div}
                    </div>
                    <br>
                    <br>
                </body>
                </html>
                '''
        
    # Writes test results to new build_x.html file to be displayed in iframe
    results_file = copy_build(curr_ver, template)
    return results_file


def summary_to_html(readfile,writefile):
    '''
        This function reads the log file and outputs and html
        page with the summary in a table
    '''
    sidebar_template = create_sidebar()
    with open(writefile,"w") as fp:
        curr_build_file = create_test_results(readfile)

        # The formatted string holds the html template and loads in the values for content and status  
        # This templated gets injected to index.html, holding both the sidebar and test results  
        template=f'''<!doctype html>
        <html lang="en">
        <head>
            <title>Summary of Tests</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
            <style>
                    .bk-root .bk {{
                        margin: 0 auto !important;
                    }}
                    html, body {{
                        height: 100%;
                        -ms-overflow-style: none;  /* Prevent scrollbar in IE and Edge */
                        scrollbar-width: none;  /* Prevent scrollbar in Firefox */
                        overflow-x: hidden;
                        overflow-y: hidden;
                    }}
                    /* Prevent scrollbar in Chrome */
                    .html::-webkit-scrollbar {{
                        display: none;
                    }}  
                    body {{
                        border-width: 0px;
                    }}  
                    .sidebar {{
                        height: 100%; 
                        width: 175px;
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
                        font-size: 16px;
                        color: #dbdcdd;
                        display: inline-block;
                        }}
                    .sidebar a:hover {{
                        color: white;
                    }}
                    .iframe {{
                        border: none;
                        height: 100%; 
                        width: 100%;
                        padding-left: 200px; 
                    }}
                    /* On screens that are less than 700px wide, make the sidebar into a topbar */
                    @media screen and (max-width: 500px) {{
                    .sidebar {{
                        display: none;
                    }}
                    }}
            </style>
        </head>
        <body>
            <div class="sidebar">
                {sidebar_template}
            </div>
            <iframe class="iframe" src={curr_build_file} name="results_iframe"></iframe>
            <script src='version.js'>
            </script>
        </body>
    </html>
        '''
        shutil.copy("version.js", f"{gh_pages}/docs")
        fp.write(template)

def write_to_csv(readfile):
    '''
        This function is used to store data between builds into a csv
    '''

    total=sum(x[1] for x in get_times(readfile).items()) #

    data=create_summary(readfile)
    data["Time Taken"]=total/60
    local_time = str(int(time.time()))  #datetime.today().strftime('%s') to convert to unix timestamp instead of a
    data["Date"] = local_time
    data["Build Number"] = curr_ver
    # normal date format. This helps in plotting as all x axis elements are now unique
    #local_time+=f"({curr_ver})"
    data["Compile Time Warnings"]=get_compile(f"{gh_pages}/records/version_{curr_ver}/build_{curr_ver}.log")
    fields = ["Date", "Total available tests", "Unrunnable tests",
              "Runnable tests", "Total number of thorns",
              "Number of tested thorns", "Number of tests passed",
              "Number passed only to set tolerance", "Number failed",
              "Time Taken", "Compile Time Warnings", "Build Number"]
    with open(f"{gh_pages}/test_nums.csv",'a') as csvfile:
        if csvfile.tell() == 0:
            csvfile.write(",".join(fields) + "\n")
        csvfile.write(",".join([str(data[key]) for key in fields]) + "\n")
#import glob, glob.glob("records/*/"build_1_2_*")


if __name__ == "__main__":

    for i in range(get_version()-1, -1, -1):
        # Ascending order from build 1 to the latest
        count = get_version()-i
        # Sets the curr_version, curr and last record files
        set_curr_version(count)
        write_to_csv(curr)
        summary_to_html(curr,f"{gh_pages}/docs/index.html")
        test_comparison=test_comp(curr,last)
        if len(test_comparison["Failed Tests"])!=0 or len(test_comparison["Newly Passing Tests"])!=0 :
            dir = os.path.split(__file__)[0]
