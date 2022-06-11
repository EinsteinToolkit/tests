var membersFile = new XMLHttpRequest();
membersFile.open("GET", "version.txt", false);
membersFile.send();
lines = membersFile.responseText.split("\n")

// assuming it's a github.io page the first part of the FQDN is the username on
// github
user = window.location.host.split('.')[0]
text='<img src="https://github.com/'+user+'/einsteintoolkit/actions/workflows/main.yml/badge.svg" style="display:block;margin-left: auto;margin-right: auto;">';

lines.forEach(element => {
    text+='<a href="index_'+element+'.html">Build #'+element+'</a>'
});
    
    

sidebar=document.getElementsByClassName('sidebar');
sidebar[0].innerHTML=text;
