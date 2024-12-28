function loadScript(src, isLocal) {
    return new Promise((resolve, reject) => {
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        
        if (isLocal) {
            
            document.head.appendChild(script);
        } else {
            // For CDN scripts, change to  crossorigin
            script.crossOrigin = 'anonymous';
            document.head.appendChild(script);
        }
    });
}

// Load the scripts
loadScript('https://code.jquery.com/jquery-3.5.1.min.js', false)
    .then(() => loadScript('https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js', false))
    .then(() => loadScript('https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js', false))
    .then(() => loadScript('/static/js/main.js', true))
    .catch(error => console.error('Script loading failed', error));
