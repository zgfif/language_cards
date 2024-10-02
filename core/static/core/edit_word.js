
function translate_the_text(csrf_token, text, studying_lang='en') {
    $.ajax({
      url: '/translate',
      type: 'POST',
      headers: {'X-CSRFToken': csrf_token},
      contentType: 'application/json',
      data: JSON.stringify({source_lang: studying_lang, text: text}),
      dataType: 'json',
      success: function(data) {
        // Handle the successful response here
        const translation = data['translation'];
        // if receive data set "translation" input of /add_word form
        $('input[name="translation"]').val(translation);
      },
      error: function(xhr, status, error) {
        // Handle errors here
        console.error(xhr.responseText);
      }
    });
}


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
	  sentence = $('#id_sentence'),
          updateBtn = $('#update_button');
	  csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
	  studyingLangFull = $('#sl').attr('data-sl-full').toLowerCase();
   
    // set placeholder depending from current studying language
    word.attr('placeholder', `to ${studyingLangFull}`);
    sentence.attr('placeholder', `example of sentence in ${studyingLangFull}`);
    

    // after loading the form the "update" button is inactive
    disableBtn(updateBtn);

    // this is the text in word input after loading the page
    const initialWord = word.val();

    // when we change the word we make request to db if the user has record with this word
	// if we have with this word then  the word is not "UNIQUE"
	// and show correspoding alert('you already have this "word" in db')
	// else we make "update" button enabled.


    function validateUniquenessOfWord(btn, word='') {
	authToken = $('#sl').attr('data-auth_token');
	studyingLang = $('#sl').attr('data-sl-short');;
	
	if (word != '') {
		    $.ajax({
      	    		url: `/api/words/?exact_word=${word}`,
      	    	    	type: 'GET',
      	    	    	headers: {'Authorization': `Token ${authToken}`},
      	    	    	success: function(data) {
				if (data['count'] > 0) {
					disableBtn(updateBtn);
		    	    		 alert(`You have already added "${word}" to your dictionary`);
	        		} else { 
					enableBtn(updateBtn);
					translate_the_text(csrfToken, word, studyingLang);
				} 
      	    	    	},
      	    	    	error: function(xhr, status, error) {
        			console.error(xhr.responseText);
      	    	    	}
    	    	    });


	} else { console.log('no word to valiate uniqueness')}
    }


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
	      updateBtn = $('#update_button');

	if (currentWord == initialWord) {
	    enableBtn(updateBtn);
	} else if (currentWord == '') {
	    disableBtn(updateBtn);
	} else {
	     validateUniquenessOfWord(updateBtn, currentWord);
	}
	
    }
});


