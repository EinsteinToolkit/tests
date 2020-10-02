from cactusjenkins.testtable.testtable import read_file
import sys
import os,csv,time,requests
from datetime import datetime
import matplotlib.pyplot as plt
import bokeh.plotting as bplt
import bokeh.models.tools as btools
import bokeh.models.callbacks as bcall
from bokeh.resources import CDN
from bokeh.embed import components
# This part finds the second log file in the folder
log=""
logs=[]
for fp in os.listdir("./"):
    if fp.endswith(".log"):
        log=os.path.join("./", fp)
        logs.append(log)
records=os.listdir("./records")
last=records[len(records)-1]
ext=last.find(".log")
num=int(last[ext-1:ext])





def create_summary(file):
    '''
        This function parses the test results from the build__2_1.log file
        into a dictionary
    '''
    sum_data={}
    with open(file,"r") as fp:
        lines=fp.read().splitlines()
        # Find the line where the summary starts
        sum_start=lines.index("  Summary for configuration sim")+6
        i=sum_start
        # Loop until the end of the summary
        while lines[i]!="  Tests passed:":
            # The spacing of this line is unique and as such requires a special if statement
            if lines[i]=="    Number passed only to" and lines[i]!="":
                split_l=lines[i+1].split("->")
                split_l[0]=lines[i]+" "+split_l[0]

                # Convert numerical data to integer
                try:
                    sum_data[" ".join(split_l[0].split())]=int(split_l[1].strip())
                except:
                    sum_data[" ".join(split_l[0].split())]=split_l[1]
                # This data field has to lines and as such increment the line counter twice
                i+=1

            # The regular line parsing code
            elif lines[i]!="":
                split_l=lines[i].split("->")
                try:
                    sum_data[" ".join(split_l[0].split())]=int(split_l[1].strip())
                except:
                    sum_data[" ".join(split_l[0].split())]=split_l[1]
            i+=1
            
    return sum_data
    



def get_tests(readfile):
    '''
        This functions reads the names of the tests that failed and passed
        from the log files and returns the set of them in tuples.
    '''
    passed=set()
    failed=set()
    with open(readfile,"r") as fp:
        lines=fp.read().splitlines()
        ind=lines.index("  Tests passed:")+2
        while lines[ind]!="  Tests failed:" and lines[ind]!="========================================================================":
            passed.add(" ".join(lines[ind].split()))
            ind+=1
        ind+=2
        while ind<len(lines) and lines[ind]!="========================================================================":
            failed.add(" ".join(lines[ind].split()))
            ind+=1
        if "" in passed:
            passed.remove("")
        if "" in failed:
            failed.remove("")
    return passed,failed



def test_comp(readfile_new,readfile_old):
    '''
        This function compares the tests from the previous run 
        to see which failed, which failed this time but did
        not in the last, which passed this time but not in the last,
        and the new and removed tests.
    '''
    passed_n,failed_n=get_tests(readfile_new)
    passed_o,failed_o=get_tests(readfile_old)
    newly_p=passed_n-passed_o
    newly_f=failed_n-failed_o
    new_tests=(passed_n.union(failed_n))-(passed_o.union(failed_o))
    missing_tests=(passed_o.union(failed_o))-(passed_n.union(failed_n))
    types=["Failed Tests","Newly Passing Tests","Newly Failing Tests","Newly Added Tests", "Removed Tests"]
    tests=[failed_n,newly_p,newly_f,new_tests,missing_tests]
    test_dict={types[i]:tests[i] for i in range(len(types))}
    return test_dict

commit_list=requests.get("https://api.github.com/repos/mojamil/einsteintoolkit/commits")
response=commit_list.json()
current=response[0]["sha"]
previous=response[1]["sha"]
compare=requests.get(f"https://api.github.com/repos/mojamil/einsteintoolkit/compare/{previous}...{current}")
diff=compare.json()["diff_url"]

log_link=f"https://github.com/mojamil/einsteintoolkit/blob/master/records/{last[ext-1:]+str(num+1)}"
def gen_report(readfile):
    '''
        This function generates the html table that shows
        the comparison of test logs from last version generated
        by test_comp
    '''
    test_comparison=test_comp(readfile,"./records/"+last)
    output='''<table style="border: 1px solid black;margin-left: auto;margin-right: auto;">\n'''
    for result in test_comparison.keys():
        if(result!="Failed Tests"):
            output+=f"<tr><th><a href='{diff}'>"+result+"</a></th></tr>\n"
        else:
            output+=f"<tr><th><a href='{log_link}'>"+result+"</a></th></tr>\n"
        if(len(test_comparison[result])==0):
            output+="<tr><td></td></tr>"

        for test in test_comparison[result]:
            output+=f"  <tr><td>{test}</td></tr>\n"
    
    output+="</table>"
    return output

def get_times(readfile):
    '''
        This function finds the times taken for each test in the log
        file and then stores that in a dictionary and then sorts
        those tests in descending order by time
    '''
    times={}
    with open(readfile,"r") as fp:
        lines=fp.read().splitlines()
        ind=lines.index("  Details:")+2
        while lines[ind] !="  Thorns with no valid testsuite parameter files:":
            try:
                time_i=lines[ind].index('(')
                tim=float(lines[ind][time_i+1:].split()[0])
                test_name=lines[ind][:time_i-1].split()[0]
                times[test_name]=tim
            except:
                pass
            ind+=1

    return {test:ti for test,ti in sorted(times.items(),key= lambda x : x[1],reverse=True)} # This is a dictionary comprehension that uses sorted to order the items in times.items() into a dictionary

def exceed_thresh(time_dict,thresh):
    '''
        This function finds tests that exceed a certain time threshhold
    '''
    return {test:ti for test,ti in time_dict.items() if ti>thresh}


def longest_tests(time_dict,num_tests):
    '''
        This function finds the tests that took the longest time.
        It returns a dictionary of the num_test number of longest
        tests.
    '''
    longest={}
    i=0
    for item in time_dict.items():
        if i>num_tests-1:
            break
        longest[item[0]]=item[1]
        i+=1
    return longest

def gen_time(readfile):
    time_dict=get_times(readfile)
    output=''' <table style="border: 1px solid black;margin-left: auto;margin-right: auto;">\n'''
    output+="<tr><th>Longest Tests</th></tr>\n"
    for times in longest_tests(time_dict,10).keys():
        output+=f"  <tr><td>{times}</td><td>{time_dict[times]}s</td></tr>\n"
    output+="</table><br>"
    output+='''<table style="border: 1px solid black;margin-left: auto;margin-right: auto;">\n'''
    output+="<tr><th>Tests That Take More Than 20s</th></tr>\n"
    for times in exceed_thresh(time_dict,20).keys():
        output+=f"  <tr><td>{times}</td><td>{time_dict[times]}s</td></tr>\n"
    output+="</table>"
    return output

def plot_test_data():
    dat=list(get_data("Runnable tests").values())
    times=list(get_data("Number of tests passed").keys())
    dat1=list(get_data("Number of tests passed").values())
    print(dat)
    src=bplt.ColumnDataSource(data=dict(
        t=times,
        rt=dat,
        tp=dat1,
        xax=[0]*len(times),
        url=["./docs/index.html"]*len(times),
    ))
    TOOLTIPS = [
        ("Tests Passed", "$tp"),
    ]
    print(src.data["rt"])
    p=bplt.figure(x_range=times,plot_width=600, plot_height=600,tools="tap",
           title=None, toolbar_location="below")
    p.circle(times,dat,size=10,color="green")
    p.circle('t','tp',size=10,color="blue",source=src)
    url = "@url"
    taptool = p.select(type=btools.TapTool)
    taptool.callback = bcall.OpenURL(url=url)
    p.varea(y1='rt',y2='xax', x='t', color="green",source=src,alpha=0.5)
    p.varea(y1='tp',y2='xax', x='t', color="blue",source=src,alpha=0.5)
    
    script, div = components(p)
    
    return script,div

def summary_to_html(readfile,writefile):
    '''
        This function reads the log file and outputs and html
        page with the summary in a table
    '''

    data=create_summary(readfile)
    
    contents=""
    script,div=plot_test_data();

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
            contents+=f"        <tr><td>{key}</td><td>{data[key]}</td><tr>\n"

        # The formatted string holds the html template and loads in the values for content and status    
        template=f'''<!doctype html>
    <html lang="en">
        <head>
            <title>Summary of Tests</title>
            <style>
            .bk-root .bk {{
                margin: 0 auto !important;
            }}
            </style>
            <script src="https://cdn.bokeh.org/bokeh/release/bokeh-2.0.1.min.js"
            crossorigin="anonymous"></script>
            {script}
        </head>
        <body>
            <h1 style="text-align:center">{status}</h1>
            <table style="border: 1px solid black;margin-left: auto;margin-right: auto;">
            {contents}
            </table>
            <br>
            {gen_report(readfile)}
            <br>
            {gen_time(readfile)}
            <br>
            <table style="margin: 0 auto;">
                {div}
            </table>
            
            
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
    with open('test_nums.csv','a') as csvfile:
        contents=f"{local_time}"
        for key in data.keys():
            contents+=f",{data[key]}"
        contents+="\n"
        csvfile.write(contents)

#write_to_csv(log)

def plot_data(name,data,dates):
    plt.xlabel("Date of Test")
    plt.ylabel(name)
    plt.plot(dates,data,'bo-')
    plt.fill_between(dates,0,data,facecolor='blue',alpha=0.3)
    plt.savefig("./docs/plot.png")


def get_data(name):
    data={}
    with open('test_nums.csv','r') as csvfile:
        fields=csvfile.readline().strip().split(",")
        name_i=fields.index(name)
        line=csvfile.readline()
        while line !="":
            entry=line.strip().split(",")
            data[entry[0]]=float(entry[name_i])
            line=csvfile.readline()
    return data






summary_to_html(log,"docs/index.html")

command='''for file in *log;do cp "$file" "./records/${file%.log}_'''+str(num+1)+'''.log";done'''
#os.system(command)




