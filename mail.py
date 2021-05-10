import requests
import os
from store import get_version

runs_list=requests.get("https://api.github.com/repos/mojamil/einsteintoolkit/actions/runs").json()
commit_list=requests.get("https://api.github.com/repos/mojamil/einsteintoolkit/commits")
response=commit_list.json()

current=response[0]["sha"]
previous=runs_list["workflow_runs"][1]["head_commit"]['id']

compare=requests.get(f"https://api.github.com/repos/mojamil/einsteintoolkit/compare/{previous}...{current}")
commits=compare.json()["commits"]


workflows=requests.get("https://api.github.com/repos/mojamil/einsteintoolkit/actions/runs")
run_id=workflows.json()['workflow_runs'][0]["id"]

# jobs_list=requests.get(f"https://api.github.com/repos/mojamil/einsteintoolkit/actions/runs/{run_id}/jobs")
# jobs=jobs_list.json()["jobs"]
# build_job=jobs[0]["steps"][3]
build_no=get_version()-1
messages=""
for commit in commits:
    messages+=commit["commit"]["message"]+"\n"

content=f'''Test
Build URL: https://mojamil.github.io/einsteintoolkit/index_{build_no}
Project:EinsteinToolkit
Date of build:{commits[0]["commit"]["committer"]["date"]}
Changes

{messages}

'''
# Import smtplib for the actual sending function
import smtplib
 
# Import the email modules we'll need
from email.message import EmailMessage
 
# Create a text/plain message
msg = EmailMessage()
msg.set_content(content)
 
msg['Subject'] = 'A demo email'
msg['From'] = "jenkins@build-test.barrywardell.net"
msg['To'] = "test@einsteintoolkit.org"
 
# Send the message via our own SMTP server.
s = smtplib.SMTP('mail.einsteintoolkit.org')
s.send_message(msg)
s.quit()