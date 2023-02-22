# Einstein Toolkit Automated Testing Using Github Actions

- [Einstein Toolkit Automated Testing Using Github Actions](#einstein-toolkit-automated-testing-using-github-actions)
  - [Introduction](#introduction)
    - [What is Github Actions](#what-is-github-actions)
    - [Why Github Actions](#why-github-actions)
    - [Important Setup](#setup)
    - [File Overview](#file-overview)
  - [Explanation of Files](#explanation-of-files)
    - [main.yml](#mainyml)
    - [logparser](#logparser)
    - [store](#store)
    - [logpage](#logpage)
    - [regenerate](#regenerate)
    - [create_csv](#create_csv)
    - [i-frames and badge](#sidebar.html)
  
## Introduction

### What is Github Actions

Github Actions is continuous integration/ continous development platform that runs
a set of commands on a repository. Github Actions allows the creation of user 
created modules that automates certain commonly used workflows. On each push, the 
workflow is run in a docker container (running ubuntu).

### Why Github Actions

- Github Actions allows tests to be run on their servers as such there is no server maintenance required
- There is less security risks because its hosted on the cloud rather than an active server
- Easier local testing allowing for new features to be tested easier
- Flexibility to to tailor the reports to the Einstein Toolkit since we can design our own parsers and tools.
- Larger community giving more opportunity for more plugins than Jenkins.

### Setup
In orer to make workflow function correctly, a secret needs to be stored on this repo with
the name PERSONAL_TOKEN. In order to create the token follow this guide: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token.
After creating the token it can be stored as shown here https://docs.github.com/en/actions/reference/encrypted-secrets.


### File Overview

master:
- `main.yml` - Executes the workflow

scripts:
- `build-and-test.sh` - Compiles and runs the tests
- `logparser.py` - Parses the log files
- `logpage.py` - Generates the HTML pages
- `store.py` - Stores logs for future use
- `mail.py` - Send email each time tests are run
- `regenerate.py` - Used to regenerate all HTML pages when new design is created
- `create_csv.py` - Used to recreate CSV files when new columns are added

gh-pages:
- `test_nums.csv` - Stores summary stats from logs
- `records/` - Folder contains compilation logs, logs with summary of tests, and individual test logs and diffs. 
- `docs/index.html` - HTML page that is displayed on mojamil.github.io/einsteintoolkit/

## Explanation of Files

### main.yml

This file contains the steps for the workflow that need to be executed.
It checks if any jobs are running currently, sets up the environment,
and pushes all the generated log and html files to the repository.

The workflow is run on each push and can also be run manually

The first part of the workflow is checking if there is already a workflow run in progress, and if that is true, this new run is put into a pending state. If there exists a pending run and the workflow is triggered, the pending workflow is cancelled, and the new workflow has pending status.
We use github concurrency to acheive this: https://docs.github.com/en/actions/using-jobs/using-concurrency

![skipping-code](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/conc-manual.png)

The CI runner checks-out both the scripts branch (contains the scripts are to parse and output the data) and the gh-pages branch (contains test log files and HTML output).

![check-out](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/check-out.png)

It is important to note that for every workflow run, a link to the master branch and gh-pages branch have to be passed. This done to minimize hardcoding of the workflow and help improve transferability of the testing framework.

Then, all the required libraries are installed, after which a clone of the master branch is created and the files from the gh-pages and scripts 
branches are copied over into a new repository on GitHub's cloud and run:

![copy](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/libraries.png)

Then the files with the data that needs to be stored are copied back and pushed to the remote gh-pages branch.

In order check if there was a workflow run that was cancelled the workflow
checks if there were in any changes made to the repository and if so it runs
the workflow again. This workflow would be run again using this plugin: https://github.com/benc-uk/workflow-dispatch

![check](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/check.png)

### logparser

This python script is used to parse the log files for required data.
The parsing is done by using regex expression matching to find the
necessary information. Initially, logparser looks through the arguments provided for the master and gh-pages branch.

A brief description of what each function does:

`create_summary(file)` This function looks for the summary of the tests stored in log files such
as build__2_1.log or build__1_2.log:

![summary](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/summary.png)

`get_tests(file)` Gets the name of the test that passed and failed as listed in log files such
as build__2_1.log or build__1_2.log:

![pass-fail](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/pass-fail.png)

`test_comp(file1,file2)` Compares the passed and failed tests from file1 and file2 and returns
which files are newly passing,newly failing, newly added and removed.

`get_times(file)` This function finds the times taken for each test in the log
file and then stores that in a dictionary and then sorts those tests in descending order by time

`exceed_thresh(time_dict,thresh)` This function finds tests that exceed a certain time threshhold

`longest_tests(time_dict,num_tests)` This function uses output from get_times i.e. time_dict to find
num_tests number of the longest test

`get_unrunnable(file)` This test reads the log file looking for tests that could not be run
and the corresponding reason.

![thorns](https://github.com/mojamil/einsteintoolkit/blob/gh-pages/images/thorns.png) ![procs](https://github.com/mojamil/einsteintoolkit/blob/gh-pages/images/processors.png)

`get_data(file)` Retrieves singular field of data from a csv and returns it as a list

`get_warning_thorns(file)` Looks at the compile log and searches for compilation warnings
and outputs the number of warnings per thorn:

![comperr](https://github.com/mojamil/einsteintoolkit/blob/gh-pages/images/comperr.png)

`get_compile(file)` Gets the total number of compilation warnings

`get_warning_type(file)`  Compiles of counts of what types of warnings are produced the most
 during compilation

`get_warning_thorns(file)` This code finds how many compile time warnings are related each thorn

### store

`copy_tests(test_dir,version,procs)`  copies logs and diffs for each test. test_dir is where the test logs and diffs are.The version number and number of procs is used to store the files as shown below:

![vers_proc](https://github.com/mojamil/einsteintoolkit/blob/gh-pages/images/vers_proc.png)

`copy_logs(test_dir, version)` This copies the test logs for future use

`copy_build(version, test_results, store = None)` This copies the old html build files showing test results for future use

`copy_compile_log(version)` This copies the compilation logs for future use

`store_commit_id(version)` This stores the current git HEAD hash for future use

`get_version(store = None)` Gets the version based on the stored files if there are no stored files returns 1

`store_version(next_build)` This stores the version of the current build in the list of build numbers file.

`get_commit_id(version, store = None)` This returns the code commit id that this version corresponds to.

### logpage

Logpage.py generates tables for the html report page and outputs as an html page as
shown here:
https://einsteintoolkit.github.io/tests/


This file gets the last few commits using githubs REST API for commits and workflow runs as 
shown in these documentation links: https://docs.github.com/en/rest/reference/repos#commits and https://docs.github.com/en/rest/reference/actions

`gen_commits()` This function generates a list of commits that have been made since the last run. If the workflow was run manually it will say so.

![commit_table](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/commits.png)

`gen_diffs(readfile)` This function generates the html table that shows the comparison of test logs from last version generated by test_comp in logparser

`get_first_failure(test_name)` This function returns the first version number when this test failed

This table shows the table generated by gen_diffs and get_first_failure:

![gen_diffs](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/gen_diffs.png)

`gen_time(readfile)` This function generates a table with the tests that took the longest time

Before you look into the functions that generate plots, it is important to understand bokeh

This file uses bokeh, a python library, to generate plots. The plots are created using python code and bokeh
then converts to javascript and html.

![bokeh](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/bokeh.png)
![plot](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/plot.PNG)

Bokeh's plotting works similar to other plotting libraries. First a figure is generated and attributes can
be added such as tools to zoom, labels, axis ranges, etc. Bokeh plots using glyphs i.e. given data it will
plot it in the format specified for example p.line shown above generates a line graph and p.circle can be
used for scatter plots. Bokeh can show its plot locally and save it as a file or generate html and javascript
for the plot as shown below:

![bokeh2](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/bokeh2.png)

`plot_test_data(readfile)` This gets data from the csv and creates lists for each field

`gen_unrunnable(readfile)` This function generates a html showing which tests could not be run and the reason

![unrunnable](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/unrunnable.png)

`create_sidebar()` This creates sidebar.html containing all build numbers that gets injected into the HTML page created in summary_to_html

#there is a badge on the einstein toolkit website. Document on how to add this
# Put in i-frames and version.js (change extension to HTML)

![sidebar](https://github.com/EinsteinToolkit/tests/blob/gh-pages/images/sidebar.png)

`create_test_results(readfile)` This creates test results for the given log file, which gets displayed to the right of the sidebar

`summary_to_html(readfile,writefile)` This function reads the log file and outputs and html page with the summary in a table

`write_to_csv(readfile)` This function is used to store data between builds into a csv

### regenerate

This python script is used to regenerate all HTML builds in the case of design changes. This file is similar to logpage. These functions are slightly modified so that the design changes can be run in a for-loop, and hence affect all builds up to date

### create_csv

This python script is used to add columns and automate the creation of a new csv file with previous and newly added data. This file is also similar to logpage. However, since we are only modifying the CSV file, we do not use logpage functions that modify the HTML site. 
        




