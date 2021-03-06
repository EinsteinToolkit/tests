import requests,datetime,sys

def cancel_workflow(run):
    requests.post(f"https://api.github.com/repos/mojamil/einsteintoolkit/actions/runs/{run}/cancel")

def run_workflow(workflow_id):
    requests.post(f"/repos/mojamil/einsteintoolkit/actions/workflows/{workflow_id}/dispatches")

def get_currently_running():
    workflows_request=requests.get(f"https://api.github.com/repos/mojamil/einsteintoolkit/actions/workflows/main.yml/runs")
    workflows=workflows_request.json()['workflow_runs']
    currently_running=[]
    for run in workflows:
        if run['status']=='in_progress':
            currently_running.append({"workflow_id":run["workflow_id"],"created_at":run["created_at"],"updated_at":run["updated_at"]})
    return currently_running