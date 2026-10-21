'''
This file sends emails if there are failing tests or if a previously failing test passes now.
'''
import os, sys
from store import get_version
import logpage
from pygit2 import Repository

from logpage import gh_pages, repo

import requests

curr_ver = get_version(gh_pages)
baseurl = repo.remotes["origin"].url.replace("git@", "https://").replace(".git","")

readfiles = [f"{gh_pages}/records/version_{curr_ver}/build__2_{n}_{curr_ver}.log" for n in [2,1]]

status = "All Tests Passed"
number_failed = 0
data = {}
for readfile in readffiles:
  data[readfile] = logpage.create_summary(summary)
  number_failed = max(number_failed, data["Number failed"])

if number_failed!=0:
    status="Some Tests Failed"
# Add a table row for each data field
summary_contents = ""
for key in data[next(iter(data)].keys():
    summary_contents+=f"<tr><th>{key}</th><td>"
    for readfile in readfiles:
        summary_content+=f"{data[readfile][key]}</td>"
    summary_content+="<tr>\n"

html = f'''<!doctype html>
    <html lang="en">
		<head></head>
        <body>
            <h3 style="text-align:center"><a href="{baseurl}/tree/gh-pages/records/version_{curr_ver}">Build #{curr_ver}</a></h3>
            <table class="table table-bordered " >
            <caption>Summary</caption>
            {summary_contents}
            </table>
            <table>
            <caption>Commits in Last Push</caption>
            {logpage.gen_commits()}
            </table>
            {logpage.gen_diffs(readfiles[-1])}
		</body>
	</html>
'''

subject = f"Einstein Toolkit test report: {status}"

r = requests.post('https://www.einsteintoolkit.org/hooks/tests_finished.php?secret=ntdUMP30w0lR3KqXzZds7mftkZox8CHO23',
                   json={"subject": subject, "message": html})

sys.exit(0 if r.status_code == 200 else 1)
