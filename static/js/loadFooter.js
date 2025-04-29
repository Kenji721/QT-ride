// loadFooter.js
document.addEventListener('DOMContentLoaded', function() {
    fetch('/static/footer.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('footer-placeholder').innerHTML = data;
        });
});