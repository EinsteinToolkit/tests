try {
    var workflowFile = new XMLHttpRequest();
    workflowFile.open("GET", "https://api.github.com/repos/EinsteinToolkit/tests/actions/runs", false);
    workflowFile.send();

    var jsonResponse = JSON.parse(workflowFile.responseText);
    count = jsonResponse["total_count"];
    if (count > 0) {
        latest_run = jsonResponse["workflow_runs"][0];
        console.log(latest_run);
        stat = latest_run.status; // completed, requested, in-progress
        conclusion = latest_run.conclusion; // success, failure
    }
} catch (e) {
  console.log(e.message);
}

if (conclusion == "failure") {
    badge_to_display = "failing-status.svg"
} else if (stat == "completed") {
    badge_to_display = "passing-status.svg" 
} else {
    badge_to_display = "pending-status.svg" 
}

try {
    sidebar = document.getElementsByClassName('workflow-status');
    sidebar[0].innerHTML = '<img src="' + badge_to_display + '" style="display:block; margin-left: auto; margin-right: auto;">';
} catch (err) {
    console.log(err);
}
