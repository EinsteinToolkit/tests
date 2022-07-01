from collections import defaultdict
import re
import glob
from datetime import datetime, timezone
list_of_builds = []
curr_ver = 0
for i in range(1, 254):
    curr_ver = i
    curr = f"./records/version_{curr_ver}/build__2_1_{curr_ver}.log"
    list_of_builds.append(glob.glob(curr))

no_of_builds = []
for i in range(1, 254):
    no_of_builds.append(i)
b = [] # new list that is in ascending order of builds
for k in no_of_builds:
    for i in range(len(list_of_builds)): # double loop to iterate through the entire list of
        split = list_of_builds[i][0].split("/")
        build_no = int(split[2][8::]) # we get the build number from the string this way
        if k == build_no:
            b.append(list_of_builds[i])
            break
no_of_builds.clear()
for i in range(len(b)): # changing the list from lis[list] to list[string]
    no_of_builds.append(b[i][0])
list_of_builds = no_of_builds
#print(list_of_builds)

def stuff_to_write(file):
    with open(file, "r") as fp:
        lines = fp.read().splitlines()
        j = 0
        while not re.match("^\s*Summary for configuration sim", lines[j]):
            j += 1
        sum_data = {}
        j += 6
        # Loop until the end of the summary
        while not re.match("\s*Tests passed:", lines[j]):
            # The spacing of this line is unique and as such requires a special if statement
            if re.match("\s*Number passed only to\s*", lines[j]) and lines[j] != "":
                split_l = lines[j + 1].split("->")
                split_l[0] = lines[j] + " " + split_l[0]

                # Convert numerical data to integer
                try:
                    sum_data[" ".join(split_l[0].split())] = int(split_l[1].strip())
                except:
                    sum_data[" ".join(split_l[0].split())] = split_l[1]
                # This data field has to lines and as such increment the line counter twice
                j += 1

            # The regular line parsing code
            elif lines[j] != "":
                split_l = lines[j].split("->")
                try:
                    sum_data[" ".join(split_l[0].split())] = int(split_l[1].strip())
                except:
                    sum_data[" ".join(split_l[0].split())] = split_l[1]
            j += 1
        #print(sum_data)
        return sum_data

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
    return sum(warning_types.values())


with open('test_nums.csv','w+') as csvfile:  # Writing the headings for the csv file.
    a = f"Date"
    a += f",Total available tests"
    a += f",Unrunnable tests"
    a += f",Runnable tests"
    a += f",Total number of thorns"
    a += f",Number of tested thorns"
    a += f",Number of tests passed"
    a += f",Number passed only to set tolerance"
    a += f",Number failed"
    a += f",Time Taken"
    a += f",Compile Time Warnings"
    a += f",Build Number"
    a += "\n"
    csvfile.write(a)

for i in range(len(list_of_builds)):  # Writing the data in the new csv file.
    file = list_of_builds[i]
    total = sum(x[1] for x in get_times(file).items()) # total time taken for all the tests
    data = stuff_to_write(file) # has all the information in dictionary format until (including) Number of tests passed
    # Except the time of each test.
    data["Time Taken"] = total / 60
    data["Compile Time Warnings"] = get_warning_thorns(f"records/version_{i + 1}/build_{i + 1}.log")
    with open(file, "r") as fp:
        lines = fp.read().splitlines()
        j = 0
        bool = True
        while not re.match("^\s*Summary for configuration sim", lines[j]):  # specified according to formatting of
            # test file
            j += 1
        j += 2
        split = lines[j].split("->")  # easiest to get required value by splitting via ->
        dateString = split[1].strip() # removing spaces and end and splitting
        dateFormatter = "%a %b %d %H:%M:%S %Z %Y"
        dt = datetime.strptime(dateString, dateFormatter)  # changing format from string to datetime object
        timestamp = dt.replace(tzinfo=timezone.utc).timestamp()  # changing to UNIX seconds.
        # print(timestamp)
    with open('test_nums.csv','a') as csvfile:
        contents = f"{timestamp}"
        for key in data.keys():
            contents += f",{data[key]}"
        contents += f",{i + 1}"
        contents += "\n"
        csvfile.write(contents)





