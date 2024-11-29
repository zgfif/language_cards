// This script is used to change studying language in /profile
$(document).ready(function(){
	// authentication token we retreive from hidden input by id:
	let auth_token = $("#auth_id").val();
	
	set_selected_option();	

	// bind 'change' event on "studying lanugage" select
	$( "#id_name" ).on( "change", function() {
		let lang_val = $(this).val();

		change_studying_lang(auth_token=auth_token, language_value=lang_val);
	} );

	// this function is used to make ajax request to change studying_language	
	function change_studying_lang(auth_token=null, language_value=null) {
    		$.ajax({
			url: '/toggle_lang', 
			type: 'PATCH',
			data: {'studying_lang': language_value},
			headers: { 'Authorization': 'Token ' + auth_token}, 
			success: function(result) {
				update_current_studying_lang(value=result['full_lang_name']);
                window.location.reload();
			},
			error: function() {
				console.log('something went wrong');
			}
		});
	}

	// this function is used to update html "studying_lang" after changing
	function update_current_studying_lang(value=null) {
		$('#current_sl').text(value);
	}

	// make current studying language "selected" option
	function set_selected_option() {
		let current_sl = $('#current_sl').text();
		$(`select option:contains(${current_sl})`).prop('selected', true);
	}
});

