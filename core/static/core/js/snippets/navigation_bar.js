$( document ).ready(function() {
    $('#themeBtn').click((event) => {
        const html = $('html:first');


        if (html.attr('data-bs-theme') == 'dark') {
            html.attr('data-bs-theme', 'light');
            $(event.target).attr('src', '/static/core/images/light_btn.png');
        } else {
            html.attr('data-bs-theme', 'dark');
            $(event.target).attr('src', '/static/core/images/dark_btn.png');
        };
    });
});
