// loadHeader.js
document.addEventListener('DOMContentLoaded', function() {
    fetch('/static/header.html')
        .then(response => response.text())
        .then(data => {   
            document.getElementById('header-placeholder').innerHTML = data;
        });
});
