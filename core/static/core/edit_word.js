// this function makes the btn enabled
function enableBtn(btn) {
   btn.attr('disabled', false);
};


// this function makes the btn disabled
function disableBtn(btn) {
    btn.attr('disabled', true);
};


// assign event when the page is fully downloaded
$(document).ready(function() {
    // retrieving inputs nodes:
    const word = $('#id_word'),
          updateBtn = $('#update_button');
	  auth_token = $('#sl').attr('data-auth_token');

    // after loading the form the "update" button is inactive
    disableBtn(updateBtn);

    // this is the text in word input after loading the page
    const initialWord = word.val();

    // when we change the word we make request to db if the user has record with this word
	// if we have with this word then  the word is not "UNIQUE"
	// and show correspoding alert('you already have this "word" in db')
	// else we make "update" button enabled.



    let typingTimer;                // Timer identifier
    let doneTypingInterval = 1000;  // Time in ms (1 second)
    let $input = $('#id_word');     // Input field

    // On keyup, start the countdown
    $input.on('keyup', function () {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(doneTyping, doneTypingInterval);
    });

    // On keydown, clear the countdown 
    $input.on('keydown', function () {
        clearTimeout(typingTimer);
    });

    // User is "finished typing," do something
    function doneTyping () {
        // Do something after user has stopped typing
	const currentWord = $('#id_word').val(),
	      authToken = $('#sl').attr('data-auth_token'),
	      updateBtn = $('#update_button');
        
	    if (currentWord != '' && currentWord != initialWord) {
		    $.ajax({
      	    		url: `/api/words/?exact_word=${currentWord}`,
      	    	    	type: 'GET',
      	    	    	headers: {'Authorization': `Token ${authToken}`},
      	    	    	success: function(data) {
				if (data['count'] > 0) {
					disableBtn(updateBtn);
		    	    		 alert(`You have already added "${currentWord}" to your dictionary`);
	        		} else { enableBtn(updateBtn); } 
      	    	    	},
      	    	    	error: function(xhr, status, error) {
        			console.error(xhr.responseText);
      	    	    	}
    	    	    });
           } else if (currentWord == initialWord)
	    { enableBtn(updateBtn) } else { disableBtn(updateBtn) }
    }
});


