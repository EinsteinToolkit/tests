#!/usr/bin/env python3.2

import xml.etree.ElementTree as etree
import glob
import datetime
import os

failed_tests = set()
machines = set()
pass_machines = set()
failures = []
timestamps = {}
revision_log = {}
revision_seq = {}
num_tests = {}
num_failures = {}

def read_file(name):
    if os.path.exists(name):
        with open(name) as f:
            return f.read()
    else:
        return ""

class Test:
    def __lt__(self,other):
        if self.classname != other.classname:
            return self.classname < other.classname
        else:
            return self.name < other.name

    def __hash__(self):
        return hash(self.classname) + hash(self.name)

    def __eq__(self,other):
        return self.classname == other.classname and self.name == other.name

for infile in glob.glob("machines/*.xml"):

    machinename = infile.replace("machines/","").replace(".xml","")
    tree = etree.parse(infile)
    root = tree.getroot()

    # timestamp = read_file(infile.replace(".xml",".timestamp"))
    # timestamps[machinename] = timestamp
    revision_log[machinename] = read_file(infile.replace(".xml",".log"))
    revision_seq[machinename] = read_file(infile.replace(".xml",".seq"))

    num_tests[machinename] = 0
    num_failures[machinename] = 0

    for test in root:
        num_tests[machinename]+=1
        failure = test.find('failure')
        if failure is not None:
            machines.add(machinename)
            num_failures[machinename]+=1
            testobj = Test()
            testobj.name = test.attrib['name']
            testobj.classname = test.attrib['classname']

            failed_tests.add(testobj)

            # failed_tests.add([test.attrib['name'],
            #                   test.attrib['classname']])
            failures.append([machinename,test.attrib['name']])

    if machinename not in machines:
        pass_machines.add(machinename)
        print("No failures for {0}".format(machinename))

pass_machines = sorted(pass_machines)
machines = sorted(machines)

table = etree.Element("tests")

# def format_time(timestamp):
#     return datetime.datetime.fromtimestamp(int(timestamp),datetime.timezone.utc).strftime('%H:%M %d/%b UTC')

for machinename in machines:
    machine = etree.SubElement(
        table, "machine",
        attrib={#"rev_timestamp":format_time(timestamps[machinename]),
                "rev_log":revision_log[machinename],
                "rev_seqno":revision_seq[machinename],
                "num_tests":str(num_tests[machinename]),
                "num_failures":str(num_failures[machinename])})
    machine.text = machinename

failed_tests = sorted(failed_tests)

for testdict in failed_tests:
    testname = testdict.name
    classname = testdict.classname
    test = etree.SubElement(table, "test")

    name = etree.SubElement(test, "name")
    name.text = testname

    classname_el = etree.SubElement(test, "classname")
    classname_el.text = classname

    for machinename in machines:
        machine = etree.SubElement(test, "machine")
        machinenameel = etree.SubElement(machine, "name")
        machinenameel.text = machinename

        link="https://build.barrywardell.net/view/All/job/EinsteinToolkitMulti/lastCompletedBuild/MACHINE={0},label=master/testReport/(root)/{1}/{2}/".format(machinename,classname,testname.replace("/","_"))

        machinestate = etree.SubElement(machine, "state", attrib={"link":link})
        machinestate.text = "" if [machinename,testname] not in failures else "✗"

f = open('testtable.xml', 'wb')

f.write(etree.tostring(table))
f.close()


passtable = etree.Element("machines")

for machinename in pass_machines:
    machine = etree.SubElement(passtable, "machine", {"name":machinename})

f = open('passmachines.xml', 'wb')
f.write(etree.tostring(passtable))
f.close()
