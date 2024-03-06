var stat, conclusion, actionlink;
try {
    var workflowFile = new XMLHttpRequest();
    workflowFile.open("GET", "https://api.github.com/repos/EinsteinToolkit/tests/actions/workflows/main.yml/runs", false);
    workflowFile.send();

    var jsonResponse = JSON.parse(workflowFile.responseText);
    count = jsonResponse["total_count"];
    if (count > 0) {
        var run_number = 0;
        for(var i = 0 ; i < jsonResponse["workflow_runs"].length ; i++) {
            latestRun = jsonResponse["workflow_runs"][i];
            stat = latestRun.status; // completed, requested, in_progress
            console.log(i, " stat ", stat);
            if (stat == "completed" || stat == "in_progress") {
                run_number = i;
                console.log("run number: "+i);
                break;
            }
        }
        latestRun = jsonResponse["workflow_runs"][run_number];
        stat = latestRun.status; // completed, requested, in-progress
        conclusion = latestRun.conclusion; // success, failure, cancelled, null
        actionLink = latestRun.html_url; // link to (pending) workflow in GitHub
    }
} catch (e) {
  console.log(e.message);
}

// workflowLink = "https://einsteintoolkit.github.io/tests/";
workflowLink = actionLink;
if (stat == "completed") {
    if (conclusion == "failure") {
        badgeToDisplay = "failing-status.svg";
    } else if (conclusion == "success") {
        badgeToDisplay = "passing-status.svg";
    } else {
        badgeToDisplay = "unknown";
    }
} else if (stat == "in_progress") {
    badgeToDisplay = "pending-status.svg";
} else {
    badgeToDisplay = "unknown";
}

try {
    badgeLink = document.getElementsByClassName('workflow-status');
    badgeLink[0].innerHTML = '<a href="' + workflowLink + '" style="display:block; margin-left: auto; margin-right: auto;">' 
                         + '<img src="' + badgeToDisplay + '">'
                         + '</a>';
} catch (err) {
    console.log(err);
}
