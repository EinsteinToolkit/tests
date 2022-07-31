from collections import defaultdict
import re
import glob
from datetime import datetime, timezone

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


list_of_builds = []
for verlog in glob.glob("./records/version_*/build__2_1_*.log"):
    m = re.search("/version_([0-9]*)/", verlog)
    list_of_builds.append(int(m.group(1))-1) # "version" is one less than number in file
list_of_builds.sort()

with open('test_nums.csv','w+') as csvfile:  # Writing the headings for the csv file.
    # header
    fields = ["Date", "Total available tests", "Unrunnable tests",
              "Runnable tests", "Total number of thorns",
              "Number of tested thorns", "Number of tests passed",
              "Number passed only to set tolerance", "Number failed",
              "Time Taken", "Compile Time Warnings", "Build Number"]
    csvfile.write(",".join(fields) + "\n")

    for buildnum in list_of_builds:  # Writing the data in the new csv file.
        print("generating data for build ",buildnum," out of ",len(list_of_builds))
        file = f"records/version_{buildnum + 1}/build__2_1_{buildnum + 1}.log"
        total = sum(x[1] for x in get_times(file).items()) # total time taken for all the tests
        data = stuff_to_write(file) # has all the information in dictionary format until (including) Number of tests passed
        # Except the time of each test.
        data["Time Taken"] = total / 60
        data["Compile Time Warnings"] = get_warning_thorns(f"records/version_{buildnum + 1}/build_{buildnum + 1}.log")
        with open(file, "r") as fp:
            lines = fp.read().splitlines()
            j = 0
            while not re.match("^\s*Summary for configuration sim", lines[j]):  # specified according to formatting of
                j += 1
            j += 2
            split = lines[j].split("->")  # easiest to get required value by splitting via ->
            dateString = split[1].strip() # removing spaces and end and splitting
            dateFormatter = "%a %b %d %H:%M:%S %Z %Y"
            dt = datetime.strptime(dateString, dateFormatter)  # changing format from string to datetime object
            timestamp = dt.replace(tzinfo=timezone.utc).timestamp()  # changing to UNIX seconds.
            data["Date"] = f"{timestamp}"
        data["Build Number"] = f"{buildnum + 1}"
        # write new data to file
        csvfile.write(",".join([str(data[key]) for key in fields]) + "\n")
