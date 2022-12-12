try {
    var workflowFile = new XMLHttpRequest();
    workflowFile.open("GET", "https://api.github.com/repos/EinsteinToolkit/tests/actions/workflows/main.yml/runs", false);
    workflowFile.send();

    var jsonResponse = JSON.parse(workflowFile.responseText);
    count = jsonResponse["total_count"];
    if (count > 0) {
        latestRun = jsonResponse["workflow_runs"][0];
        stat = latestRun.status; // completed, requested, in-progress
        conclusion = latestRun.conclusion; // success, failure, cancelled, null
        actionLink = latestRun.html_url; // link to (pending) workflow in GitHub
    }
} catch (e) {
  console.log(e.message);
}

workflowLink = "https://einsteintoolkit.github.io/tests/";
if (conclusion == "failure") {
    badgeToDisplay = "failing-status.svg";
} else if (stat == "completed") {
    badgeToDisplay = "passing-status.svg";
} else {
    badgeToDisplay = "pending-status.svg";
    // If CI is currently pending, badge links to the action in GitHub
    workflowLink= actionLink;
}

try {
    badgeLink = document.getElementsByClassName('workflow-status');
    badgeLink[0].innerHTML = '<a href="' + workflowLink + '" style="display:block; margin-left: auto; margin-right: auto;">' 
                         + '<img src="' + badgeToDisplay + '">'
                         + '</a>';
} catch (err) {
    console.log(err);
}
