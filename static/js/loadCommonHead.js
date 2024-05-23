document.addEventListener('DOMContentLoaded', function() {
    fetch('common-head.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('common-head-placeholder').innerHTML = data;
        });
});