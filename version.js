// TODO: copy file to gh-pages branch docs/ folder

var membersFile = new XMLHttpRequest();
membersFile.open("GET", "version.txt", false);
membersFile.send();
lines = membersFile.responseText.split("\n")

// Assuming it's a github.io page the first part of the FQDN is the username on
// GitHub and the first part of the path (after the initial /) is the repo name
user = window.location.host.split('.')[0]
repo_name = window.location.pathname.split('/')[1]
text='<img src="https://github.com/'+user+'/'+repo_name+'/actions/workflows/main.yml/badge.svg" style="display:block;margin-left: auto;margin-right: auto;">';
// For indicating status for each build in sidebar using colors
build_status = document.getElementsByClassName('build-status');

lines.slice().sort((a, b) => a - b).reverse().forEach(element => {
    if (element != '') { // skips empty element at end of file
        if (build_status.innerHTML == 'Some Tests Failed' || build_status.innerHTML == 'No Tests Available') {
            // Red colored build in sidebar
            text += '<a href="index_'+ element +'.html">Build #'+ element +' style="color:indianred;" </a>'
        } else {
            // Green colored build in sidebar
            text += '<a href="index_'+ element + '.html">Build #' + element + ' style="color:lawngreen;" </a>'
        }
    }
});
    
    

sidebar=document.getElementsByClassName('sidebar');
sidebar[0].innerHTML=text;