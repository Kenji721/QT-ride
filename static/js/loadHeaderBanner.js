function loadHeaderBanner(variableContent) {
    const commonHTML = `
    
        <div class='common-container'>
            <div class="container header-content ">
                <div class="row h-100">
                    <div class="col-md-6 centralize">
                    ${variableContent}  
                    </div>
                    <div class="col-md-6 centralize">
                        <div class="right-content">
                            <img src="/static/image/Group 1387.png" alt="">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    `;

    document.addEventListener('DOMContentLoaded', function() {
        document.getElementById('loadHeaderBanner-placeholder').innerHTML = commonHTML;
    });
}