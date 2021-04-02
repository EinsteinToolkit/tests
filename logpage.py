from requests.api import get
import sys
import os,csv,time,requests
from datetime import datetime
import matplotlib.pyplot as plt
import bokeh.plotting as bplt
import bokeh.models.tools as btools
from bokeh.models import Panel, Tabs
import bokeh.models.callbacks as bcall
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.layouts import row
from store import get_version
from bokeh.palettes import viridis
from bokeh.transform import factor_cmap
from parser import create_summary,get_tests, get_warning_thorns, get_warning_type,test_comp,get_times,exceed_thresh,longest_tests,get_unrunnable,get_data,get_compile
import glob
# This part finds the second log file in the folder
log=""
logs=[]
for fp in os.listdir("./"):
    if fp.endswith(".log"):
        log=os.path.join("./", fp)
        logs.append(log)

records=os.listdir("./records")
last_ver=get_version()-1
last=f"./records/build__2_1_{last_ver}.log"


print(last_ver)

def gen_commits():
    commit_list=requests.get("https://api.github.com/repos/mojamil/einsteintoolkit/commits")
    response=commit_list.json()
    current=response[0]["sha"]
    previous=response[1]["sha"]
    compare=requests.get(f"https://api.github.com/repos/mojamil/einsteintoolkit/compare/{previous}...{current}")
    commits=compare.json()["commits"]
    out="<th>"
    count=1
    for commit in commits:
        message=commit["commit"]["message"]
        message=message.replace("\n\n","\n")
        message=message.replace('\n','<br>')
        out+="Commit "+str(count)+"</th>"
        out+="<tr> <td> Author: </td> <td>"+commit["commit"]["author"]["name"]+"</td> </tr> \n"
        out+="<tr> <td> Date: </td> <td>"+commit["commit"]["author"]["date"]+"</td> </tr> \n"
        out+="<tr> <td> Message: </td> <td>"+message+"</td> </tr> \n"
        count+=1
    return out

# log_link=f"https://github.com/mojamil/einsteintoolkit/blob/master/records/{last[ext-1:]+str(last_ver+1)}"
def gen_report(readfile):
    '''
        This function generates the html table that shows
        the comparison of test logs from last version generated
        by test_comp
    '''
    test_comparison=test_comp(readfile,last)
    output='''<table style="border: 1px solid black;margin-left: auto;margin-right: auto;">
    <caption style="text-align:center;font-weight: bold;caption-side:top">Failed Tests and Changes</caption>\n'''

    for result in test_comparison.keys():
        if(result!="Failed Tests"):
            output+=f"<tr><th>"+result+"</th></tr>\n"
        else:
            output+=f"<tr><th>"+result+"</th>"
            output+="<th>logs</th><th>diffs</th>"
        
        if(len(test_comparison[result])==0):
            output+="<tr><td></td></tr>"
        for test in test_comparison[result]:
            thorn=test.split()[-1]
            thorn=thorn[:len(thorn)-1]
            test_name=test.split()[0]
            if("Removed" not in result):
                logl=f"https://github.com/mojamil/einsteintoolkit/tree/gh-pages/records/sim_{last_ver}/{thorn}/{test_name}.log"
                diffl=f"https://github.com/mojamil/einsteintoolkit/tree/gh-pages/records/sim_{last_ver}/{thorn}/{test_name}.diffs"
                dreq=requests.get(diffl) 
                logq=requests.get(logl)   
            else:
                logl=f"https://github.com/mojamil/einsteintoolkit/tree/gh-pages/records/sim_{last_ver-1}/{thorn}/{test_name}.log"
                diffl=f"https://github.com/mojamil/einsteintoolkit/tree/gh-pages/records/sim_{last_ver-1}/{thorn}/{test_name}.diffs"
                dreq=requests.get(diffl)
                logq=requests.get(logl)
            if(logq.status_code == 200):
                output+=f"  <tr><td>{test}</td><td><a href='{logl}'>log</a></td>"
            else:
                output+=f" <tr><td>{test}</td><td>Not Available</td>"
            if(dreq.status_code == 200):
                output+=f"<td><a href='{diffl}'>diff</a></td></tr>\n"
            else:
                output+=f"<td>Not Available</td></tr>\n"  
    
    output+="</table>"
    return output


def gen_time(readfile):
    time_dict=get_times(readfile)
    output='''<table style="border: 1px solid black;margin-left: auto;margin-right: auto;">
    <caption style="text-align:center;font-weight: bold;caption-side:top">Longest Tests</caption>\n'''
    output+="<tr><th>Test Name</th><th>Running Time</th>"
    for times in longest_tests(time_dict,10).keys():
        output+=f"   <tr><td>{times}</td><td>{time_dict[times]}s</td></tr>\n"
    output+="</table><br>"
    return output

def plot_test_data():
    dat=list(get_data("Runnable tests").values())
    times=list(get_data("Number of tests passed").keys())
    dat1=list(get_data("Number of tests passed").values())
    dat2=list(get_data("Time Taken").values())
    cmtw=list((get_data("Compile Time Warnings").values()))

    warning_types=get_warning_thorns(f"records/build_{last_ver}.log")
    counts=list(warning_types.values())
    counts_trunc=sorted(counts,reverse=True)[:7]
    warning_types_trunc=[]
    warning_types_list=list(warning_types.keys())

    for count in counts_trunc:
        i=counts.index(count)
        warning_types_trunc.append(warning_types_list[i])
        warning_types_list.pop(i)
        counts.pop(i)
    counts=counts_trunc
    warning_types_list=warning_types_trunc
    print(warning_types_list)
    src=bplt.ColumnDataSource(data=dict(
        t=times,
        rt=dat,
        tp=dat1,
        timet=dat2,
        cmt=cmtw,
        xax=[0]*len(times),
        url=[f"./index_{x+1}.html" for x in range(last_ver)]+["index.html"]*(len(times)-last_ver),
    ))

    TOOLTIPS = [
        ("Tests Passed", "$tp"),
    ]
    print(src.data["rt"])
    p=bplt.figure(x_range=times,plot_width=1000, plot_height=600,tools="tap,wheel_zoom,box_zoom,reset",
           title="Passed Tests", toolbar_location="below")
    p.circle(times,dat,size=10,color="green")
    p.circle('t','tp',size=10,color="blue",source=src)
    url = "@url"
    taptool = p.select(type=btools.TapTool)
    taptool.callback = bcall.OpenURL(url=url)
    p.varea(y1='rt',y2='xax', x='t', color="green",source=src,alpha=0.5)
    p.varea(y1='tp',y2='xax', x='t', color="blue",source=src,alpha=0.5)
    tab1 = Panel(child=p, title="Test Results")

    p1=bplt.figure(x_range=times,plot_width=1000, plot_height=600,tools="tap,wheel_zoom,box_zoom,reset",
           title="Time Taken", toolbar_location="below")
    p1.circle('t','timet',size=10,color="blue",source=src)
    p1.line('t','timet',color="blue",source=src)
    taptool = p1.select(type=btools.TapTool)
    taptool.callback = bcall.OpenURL(url=url)
    tab2 = Panel(child=p1, title="Time Taken")

    p2=bplt.figure(x_range=times,plot_width=1000, plot_height=600,tools="tap,wheel_zoom,box_zoom,reset",
           title="Time Taken", toolbar_location="below")
    p2.circle('t','cmt',size=10,color="blue",source=src)
    p2.line('t','cmt',color="blue",source=src)
    taptool = p2.select(type=btools.TapTool)
    taptool.callback = bcall.OpenURL(url=url)
    tab3 = Panel(child=p2, title="Compile Time Warnings")

    src1=bplt.ColumnDataSource(data=dict(cts=counts,
        wts=warning_types_list))
    p3=bplt.figure(x_range=warning_types_list,plot_width=1200, title="Compilation Warning Thorns",
           toolbar_location="below", tools="tap,wheel_zoom,box_zoom,reset")
    p3.vbar(x='wts', top='cts', width=0.9, source=src1,
       line_color='white', fill_color=factor_cmap('wts', palette=viridis(len(counts)), factors=warning_types_list))
    tab4=Panel(child=p3, title="Compilation Warning Thorns")

    script, div = components(Tabs(tabs=[tab1, tab2,tab3,tab4]))
    
    return script,div


def gen_unrunnable(readfile):
    m,n=get_unrunnable(readfile)
    output=''' <table style="border: 1px solid black;margin-left: auto;margin-right: auto;">
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
    script,div=plot_test_data()
    print(div)

    # Check Status Using the data from the summary
    status="All Tests Passed"
    if data["Number of tests passed"]==0:
        status="All Tests Passed"
    elif data["Number failed"]!=0:
        status="Some Tests Failed"
        # Send email if tests failed
        #os.system(f'python3 mail.py')
    sidebar=gen_sidebar()
    with open(writefile,"w") as fp:
        for key in data.keys():

            # Add a table row for each data field
            contents+=f"        <tr><td>{key}</td><td>{data[key]}</td><tr>\n"

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
                background-color: #111; 
                overflow-x: hidden;
                padding-top: 20px;
            }}
            .sidebar a {{
                padding: 6px 8px 6px 16px;
                text-decoration: none;
                font-size: 18px;
                color: lightgray;
                display: block;
                }}
            .sidebar a:hover {{
                color: #f1f1f1;
            }}
                        /* On screens that are less than 700px wide, make the sidebar into a topbar */
            @media screen and (max-width: 700px) {{
            .sidebar {{
              width: 100%;
              height: auto;
              position: relative;
            }}
            .sidebar a {{float: left;}}
            }}
            /* On screens that are less than 400px, display the bar vertically, instead of horizontally */
            @media screen and (max-width: 400px) {{
            .sidebar a {{
              text-align: center;
              float: none;
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
                <img src="https://github.com/mojamil/einsteintoolkit/actions/workflows/main.yml/badge.svg" style="display:block;margin-left: auto;margin-right: auto;">
                <h3 style="text-align:center">Build #{last_ver+1}</h3>
                <table style="border: 1px solid black;margin-left: auto;margin-right: auto;">
                <caption style="text-align:center;font-weight: bold;caption-side:top">Summary</caption>
                {contents}
                </table>
                <br>
                <table style="border: 1px solid black;margin-left: auto;margin-right: auto;">
                <caption style="text-align:center;font-weight: bold;caption-side:top">Commits in Last Push</caption>
                {gen_commits()}
                </table>
                {gen_report(readfile)}
                <br>
                {gen_time(readfile)}
                <br>
                {gen_unrunnable(readfile)}
                <br>
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

    total=sum(x[1] for x in get_times(readfile).items())

    data=create_summary(readfile)
    data["Time Taken"]=total/60
    local_time = datetime.today().strftime('%Y-%m-%d')
    data["Compile Time Warnings"]=get_compile(f"records/build_{last_ver}.log")
    with open('test_nums.csv','a') as csvfile:
        contents=f"{local_time}"
        for key in data.keys():
            contents+=f",{data[key]}"
        contents+="\n"
        csvfile.write(contents)

write_to_csv(last)

def gen_sidebar():
    sidebar=""
    for i in range(last_ver,0,-1):
        sidebar+=f'''   <a href="index_{i}.html">Build #{i}</a>\n'''
    
    return sidebar
        



summary_to_html(last,"docs/index.html")
