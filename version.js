try {
    var membersFile = new XMLHttpRequest();
    membersFile.open("GET", "version.txt", false);
    membersFile.send();
    lines = membersFile.responseText.split("\n");
} catch (err) {
    console.log(err);
}

// Assuming it's a github.io page the first part of the FQDN is the username on
// GitHub and the first part of the path (after the initial /) is the repo name
user = window.location.host.split('.')[0];
repo_name = window.location.pathname.split('/')[1];

text ='<img src="https://github.com/einsteintoolkit/tests/actions/workflows/main.yml/badge.svg" style="display:block;margin-left: auto;margin-right: auto;">';

lines.slice().sort((a, b) => a - b).reverse().forEach(element => {
    if (element != '') { // skips empty element at end of file
        try {
            // Get the corresponding HTML file to check build status
            var req = new XMLHttpRequest();
            req.open("GET", "index_" + element + ".html", false);
            req.send();
            curr_html_contents = req.responseText;
            // Create dummy DOM element to parse HTML element h1
            var el = document.createElement('html');
            el.innerHTML = curr_html_contents;
            build_status = el.getElementsByTagName('h1')[0].innerHTML; 
        } catch (err) {
            console.log(err);
        }

        if (build_status == 'Some Tests Failed' || build_status == 'No Tests Available') {
            // text += '<a href="index_'+ element +'.html" style="color:indianred;"> Build #'+ element +' </a>'
            text += '<a href="index_'+ element +'.html"> Build #'+ element +' </a>'
                   + '<img src="../images/exclamation.svg" style="display: inline; width: 30px; height: 30px; float: right; margin-right: 14px;">';
        } else {
            // text += '<a href="index_'+ element + '.html" style="color:lawngreen;"> Build #' + element + ' </a>'
            text += '<a href="index_'+ element + '.html"> Build #' + element + ' </a>'
            + '<img src="../images/check.svg" style="display: inline; width: 27px; height: 27px; float: right; margin-right: 15px;">';
        }
    }
});
    
    
try {
    sidebar = document.getElementsByClassName('sidebar');
    sidebar[0].innerHTML = text;
} catch (err) {
    console.log(err);
}
