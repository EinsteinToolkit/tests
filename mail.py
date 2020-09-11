import requests

commit_list=requests.get("https://api.github.com/repos/mojamil/einsteintoolkit/commits")
response=commit_list.json()[0]
last_commit={}
last_commit["name"]=response["commit"]['author']['name']
last_commit["date"]=response["commit"]['author']['date']
last_commit["url"]=response["html_url"]
last_commit["message"]=response["commit"]["message"]
print(last_commit)

workflows=requests.get("https://api.github.com/repos/mojamil/einsteintoolkit/actions/runs")
run_id=workflows.json()['workflow_runs'][0]["id"]

jobs_list=requests.get(f"https://api.github.com/repos/mojamil/einsteintoolkit/actions/runs/{run_id}/jobs")
jobs=jobs_list.json()["jobs"]
build_job=jobs[0]["steps"][3]
# # Import smtplib for the actual sending function
# import smtplib
 
# # Import the email modules we'll need
# from email.message import EmailMessage
 
# # Create a text/plain message
# msg = EmailMessage()
# msg.set_content("Some demo body")
 
# msg['Subject'] = 'A demo email'
# msg['From'] = "jenkins@build-test.barrywardell.net"
# msg['To'] = "test@einsteintoolkit.org"
 
# # Send the message via our own SMTP server.
# s = smtplib.SMTP('mail.einsteintoolkit.org')
# s.send_message(msg)
# s.quit()