var stat, conclusion, actionlink;
stat = "unset";
try {
    var workflowFile = new XMLHttpRequest();
    workflowFile.open("GET", "https://api.github.com/repos/EinsteinToolkit/tests/actions/workflows/main.yml/runs", false);
    workflowFile.send();

    var jsonResponse = JSON.parse(workflowFile.responseText);
    count = jsonResponse["total_count"];
    if (count > 0) {
        var run_number;
        for(var i = 0 ; i < jsonResponse["workflow_runs"].length ; i++) {
            latestRun = jsonResponse["workflow_runs"][i];
            stat = latestRun.status; // completed, requested, in_progress
            console.log(i, " stat ", stat);
            if ((stat == "completed" && run_number === undefined) ||
                 stat == "in_progress" || stat == "pending") {
                run_number = i;
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
    } else if (conclusion == "cancelled") {
        badgeToDisplay = "pending-status.svg"; // cancelled b/c higher priority is queued
    } else {
        badgeToDisplay = "unknown_conclusion:" + conclusion;
    }
} else if (stat == "in_progress" || stat == "pending") {
    badgeToDisplay = "pending-status.svg";
} else {
    badgeToDisplay = "unknown_stat:" + stat;
}

try {
    badgeLink = document.getElementsByClassName('workflow-status');
    badgeLink[0].innerHTML = '<a href="' + workflowLink + '" style="display:block; margin-left: auto; margin-right: auto;">' 
                         + '<img src="' + badgeToDisplay + '">'
                         + '</a>';
} catch (err) {
    console.log(err);
}
