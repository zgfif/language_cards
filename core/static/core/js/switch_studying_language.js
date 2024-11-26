$(document).ready(function() {
    $('.languageSelect').on('click', function(event) {
        let target_language = $(event.target).data('id'),
            auth_token = $('#auth_token').data('auth_token');
        
        change_studying_lang(auth_token=auth_token, language_value=target_language);
    });
});


// this function is used to make ajax request to change studying_language	
	function change_studying_lang(auth_token=null, language_value=null) {
    		$.ajax({
			url: '/toggle_lang', 
			type: 'PATCH',
			data: {'studying_lang': language_value},
			headers: { 'Authorization': 'Token ' + auth_token}, 
			success: function() {
                //console.log(result);
                window.location.reload();
				//update_current_studying_lang(value=result['full_lang_name'])g
			},
			error: function() {
				console.log('something went wrong');
			}
		});
	}
