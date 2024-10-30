// after "create update or destroy" operation with a word we will show notification

showNotifications();

//clear all notifications after 4000 miliseconds
$('.toast').each(function() {
	setInterval(() => $(this).removeClass('show'), 4000);
});

// declaring functions:

// this function is used to show popup message after each "create update or destroy" operation
function showNotifications() {
    $('ul.messages li').each(function() {
        let txt = $(this)[0].innerText;
	$(notification(txt)).appendTo($('.toast-container'))
    });
}

// this function build notification 
function notification(text='') {
    const element = document.createElement('div');
    
    element.setAttribute('class', 'toast align-items-center text-bg-success bg-opacity-75 order-0 show');
    element.setAttribute('role', 'alert');
    element.setAttribute('aria-live', 'assertive');
    element.setAttribute('aria-atomic','true');
    element.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${text}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
            data-bs-dismiss="toast" aria-label="Close"></button>
        </div>`;
    return element;
};

