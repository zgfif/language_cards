$( document ).ready(function() {
    const cookiesTheme = retrieveThemeFromCookies();
    
    if (cookiesTheme) { applyTheme(cookiesTheme); };

    $('#themeBtn').click(() => {
        let newTheme = $('html:first').attr('data-bs-theme') == 'dark' ? 'light' : 'dark'; // retrieving new theme (value can be 'light' or 'dark')

        applyTheme(newTheme);

        saveThemeToCookies(newTheme);
    });
});



function retrieveThemeFromCookies() {
    let cookiesTheme = false;

    let cookies = document.cookie.split('; '); // retrieving cookies string and split it in array ['key=value', 'key=value']

    let cookiesObject = {};

    // convert 'key=value' pairs to objects [{'key1': 'value1'}, ...]
    for (const x of cookies) {
        pair = x.split('=');
        cookiesObject[pair[0]] = pair[1];
    };

    if (cookiesObject.hasOwnProperty('theme')) { cookiesTheme = cookiesObject['theme']; };

    return cookiesTheme;
};



function saveThemeToCookies(theme='') {
    if (theme) { document.cookie = `theme=${theme}`; }; // save new theme to cookies of browser
};



function applyTheme(theme='') {
    if (theme) {
        $('html:first').attr('data-bs-theme', theme); // set theme from cookies to page
        
        $('#themeBtn').attr('src', `/static/core/images/${theme}_btn.png`); // set theme button for current page
    };
};

