var membersFile = new XMLHttpRequest();
membersFile.open("GET", "version.txt", false);
membersFile.send();
lines = membersFile.responseText


text="";

for(i=version;i>=1;i--){
    text+='<a href="index_'+i+'.html">Build #'+i+'</a>\n'
};
sidebar=document.getElementsByClassName('sidebar');
sidebar[0].innerHTML=text;
