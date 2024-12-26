// this function translates text and pastes result into "translation" input
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



// this function is used to assign "finished typing" event listener 
// on the input ("id_word", "id_translation" or "id_sentence")
function assignFinishedTypingListener(callback, inputNode, doneTypingInterval=1000) {
    const initialInputNodeValue = inputNode.val();
    
    let typingTimeout;

    inputNode.on('keyup', function () {
	clearTimeout(typingTimeout);
        typingTimeout = setTimeout(callback, doneTypingInterval);
    });
    

    inputNode.on('keydown', function () {
        clearTimeout(typingTimeout);
    });
}


// assign event when the page is fully downloaded
$(document).ready(function() {
     
    // this function makes the btn enabled
    function enableUpdateBtn() {
       $('#update_button').attr('disabled', false);
    };


    // this function makes the btn disabled
    function disableUpdateBtn() {
       $('#update_button').attr('disabled', true);
    };

    // retrieving inputs nodes:
    const word = $('#id_word'),
	  translation = $('#id_translation'),
	  sentence = $('#id_sentence'),
	  csrfToken = $('input[name="csrfmiddlewaretoken"]').val(),
	  studyingLangFull = $('#sl').attr('data-sl-full').toLowerCase();
 

    const initialWord = word.val(),
	  initialTranslation = translation.val(),
	  initialSentence = sentence.val();
    
    // set placeholder depending from current studying language
    word.attr('placeholder', `to ${studyingLangFull}`);
    sentence.attr('placeholder', `example of sentence in ${studyingLangFull}`);
    

    // after loading the form the "update" button is inactive
    disableUpdateBtn();


    function validateUniquenessOfWord(word='') {
	authToken = $('#sl').attr('data-auth_token');
	studyingLang = $('#sl').attr('data-sl-short');
	
	if (word != '') {
		    $.ajax({
      	    		url: `/api/words/?exact_word=${word}`,
      	    	    	type: 'GET',
      	    	    	headers: {'Authorization': `Token ${authToken}`},
      	    	    	success: function(data) {
				if (data['count'] > 0) {
					disableUpdateBtn();
		    	    		 alert(`You have already added "${word}" to your dictionary`);
	        		} else { 
					enableUpdateBtn();
					translate_the_text(csrfToken, word, studyingLang);
				} 
      	    	    	},
      	    	    	error: function(xhr, status, error) {
        			console.error(xhr.responseText);
      	    	    	}
    	    	    });

	} else { console.log('no word to valiate uniqueness')}
    };


    // for "word" input
    function doneTypingWord() {
	const currentWord = $('#id_word').val();

	if (currentWord == initialWord) {
	    enableUpdateBtn();
	} else if (currentWord == '') {
	    disableUpdateBtn();
	} else {
	     validateUniquenessOfWord(currentWord);
	}
    };


    // for "translation" input
    function doneTypingTranslation() {
        // Do something after user has stopped typing
	const currentTranslation = $('#id_translation').val();
	      if (currentTranslation != initialTranslation) {
		  enableUpdateBtn();
	      }
    };
    

    // for "sentence" input
    function doneTypingSentence() {
        // Do something after user has stopped typing
	const currentSentence = $('#id_sentence').val();
	      if (currentSentence != initialSentence) {
		  enableUpdateBtn();
	      }
    };
    

    assignFinishedTypingListener(doneTypingWord, word);
    assignFinishedTypingListener(doneTypingTranslation, translation);
    assignFinishedTypingListener(doneTypingSentence, sentence);
});


