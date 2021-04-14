var membersFile = new XMLHttpRequest();
membersFile.open("GET", "version.txt", false);
membersFile.send();
lines = membersFile.responseText

var version=parseInt(lines)-1

text='<img src="https://github.com/mojamil/einsteintoolkit/actions/workflows/main.yml/badge.svg" style="display:block;margin-left: auto;margin-right: auto;">';

for(i=version;i>=1;i--){
    
    text+='<a href="index_'+i+'.html">Build #'+i+'</a>'

};
sidebar=document.getElementsByClassName('sidebar');
sidebar[0].innerHTML=text;
