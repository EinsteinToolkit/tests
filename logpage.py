from cactusjenkins.testtable.testtable import read_file
import sys
import os,csv,time,requests
# This part finds the second log file in the folder
for fp in os.listdir("./"):
    if fp.endswith(".log"):
        log=os.path.join("./", fp)


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
    


def summary_to_html(readfile,writefile):
    '''
        This function reads the log file and outputs and html
        page with the summary in a table
    '''

    data=create_summary(readfile)
    contents=""

    # Check Status Using the data from the summary
    status="All Tests Passed"
    if data["Number of tests passed"]==0:
        status="All Tests Passed"
    elif data["Number failed"]!=0:
        status="Some Tests Failed"
        # Send email if tests failed
        os.system(f'python3 mail.py')
    with open(writefile,"w") as fp:
        for key in data.keys():

            # Add a table row for each data field
            contents+=f"        <tr><td>{key}</td><td>{data[key]}</td><tr>\n"

        # The formatted string holds the html template and loads in the values for content and status    
        template=f'''<!doctype html>
    <html lang="en">
        <head>
            <title>Summary of Tests</title>
        </head>
        <body>
            <h1 style="text-align:center">{status}</h1>
            <table style="border: 1px solid black;margin-left: auto;margin-right: auto;">
            {contents}
            </table>
            
        </body>
    </html>
        '''
        fp.write(template)


summary_to_html(log,"docs/index.html")

def write_to_csv(readfile):
    '''
        This function is used to store data between builds into a csv
    '''


    data=create_summary(readfile)
    seconds=time.time()
    local_time = time.ctime(seconds)
    with open('test_nums.csv','a') as csvfile:
        contents=f"{local_time}"
        for key in data.keys():
            contents+=f",{data[key]}"
        contents+="\n"
        csvfile.write(contents)
    
write_to_csv(log)
commit_list=requests.get("https://api.github.com/repos/mojamil/einsteintoolkit/commits")
