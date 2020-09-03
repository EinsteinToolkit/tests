import sys
def create_summary(file):
    sum_data={}
    with open(file,"r") as fp:
        lines=fp.read().splitlines()
        sum_start=lines.index("  Summary for configuration sim")+6
        i=sum_start
        while lines[i]!="  Tests passed:":
            if lines[i]=="    Number passed only to" and lines[i]!="":
                split_l=lines[i+1].split("->")
                split_l[0]=lines[i]+" "+split_l[0]
                try:
                    sum_data[" ".join(split_l[0].split())]=int(split_l[1].strip())
                except:
                    sum_data[" ".join(split_l[0].split())]=split_l[1]
                i+=1
            elif lines[i]!="":
                split_l=lines[i].split("->")
                try:
                    sum_data[" ".join(split_l[0].split())]=int(split_l[1].strip())
                except:
                    sum_data[" ".join(split_l[0].split())]=split_l[1]
            i+=1
            
    return sum_data
    


def summary_to_html(readfile,writefile):
    data=create_summary(readfile)
    contents=""
    status="All Tests Passed"
    if data["Number of tests passed"]==0:
        status="All Tests Passed"
    elif data["Number failed"]!=0:
        status="Some Tests Failed"
    with open(writefile,"w") as fp:
        for key in data.keys():
            contents+=f"        <tr><td>{key}</td><td>{data[key]}</td><tr>\n"
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
summary_to_html("build__2_2.log","docs/index.html")