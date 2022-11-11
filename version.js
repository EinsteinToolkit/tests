try {
    var membersFile = new XMLHttpRequest();
    membersFile.open("GET", "sidebar.html", false);
    membersFile.send();
    content = membersFile.responseText;
} catch (err) {
    console.log(err);
}

try {
    sidebar = document.getElementsByClassName('sidebar');
    sidebar[0].innerHTML = content;
} catch (err) {
    console.log(err);
}