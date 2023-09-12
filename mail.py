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
summary=f"{gh_pages}/records/version_{curr_ver}/build__2_1_{curr_ver}.log"
baseurl = repo.remotes["origin"].url.replace("git@", "https://").replace(".git","")

data = logpage.create_summary(summary)
status = "All Tests Passed"
if data["Number failed"]!=0:
    status="Some Tests Failed"
# Add a table row for each data field
contents = "\n".join([f"<tr><th>{key}</th><td>{data[key]}</td><tr>" for key in data.keys()])

html = f'''<!doctype html>
    <html lang="en">
		<head></head>
        <body>
            <h3 style="text-align:center"><a href="{baseurl}/tree/gh-pages/records/version_{curr_ver}">Build #{curr_ver}</a></h3>
            <table class="table table-bordered " >
            <caption>Summary</caption>
            {contents}
            </table>
            <table>
            <caption>Commits in Last Push</caption>
            {logpage.gen_commits()}
            </table>
            {logpage.gen_diffs(summary)}
		</body>
	</html>
'''

subject = f"Einstein Toolkit test report: {status}"

r = requests.post('https://www.einsteintoolkit.org/hooks/tests_finished.php?secret=ntdUMP30w0lR3KqXzZds7mftkZox8CHO23',
                   json={"subject": subject, "message": html})

sys.exit(0 if r.status_code == 200 else 1)
