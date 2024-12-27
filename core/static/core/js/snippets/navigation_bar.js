$( document ).ready(function() {
    let cookies = document.cookie.split(';');
    
    let obj = {}
    for (const x of cookies) {
        pair = x.split('=');
        obj[pair[0]] = pair[1]
    }

    if (obj.hasOwnProperty(' theme')) {
        const theme = obj[' theme'];
        $('html:first').attr('data-bs-theme', theme);
        $('#themeBtn').attr('src', '/static/core/images/' + theme + '_btn.png'); 
    };

    $('#themeBtn').click((event) => {
        const html = $('html:first');


        if (html.attr('data-bs-theme') == 'dark') {
            html.attr('data-bs-theme', 'light');
            $(event.target).attr('src', '/static/core/images/light_btn.png');
            document.cookie = "theme=light";
        } else {
            html.attr('data-bs-theme', 'dark');
            $(event.target).attr('src', '/static/core/images/dark_btn.png');
            document.cookie = "theme=dark";
        };
    });
});
