// this js file is used in add_word.html

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


document.addEventListener("DOMContentLoaded", (event) => {
    // retrieve csrf_token to use in request POST translate/
    const csrf_token = $('input[name="csrfmiddlewaretoken"]').val();
	
    // retrieve current studying language, i.e. 'english' or 'bulgarian'
    const sl_short = $('input[id="sl"]').attr('data-sl-short');

    // retrieve current short name studying language, i.e. 'en' or 'bg'
    const sl_full = $('input[id="sl"]').attr('data-sl-full');
	console.log(sl_short, sl_full);
    
    // change 'in english'
    $('input#id_word').attr('placeholder', 'in ' + sl_full);
    $('textarea#id_sentence').attr('placeholder', 'example of sentence in ' + sl_full);
    
    // Set focus to the input field with id "id_word"
    $("#id_word").focus();

    // this event listener is used:
    // after submitting the "add word" form the "add" button becomes disabled to prevent a second adding the same word.
    $("form").submit(function () {
        $("#add_button").attr("disabled", true);
    });

    // variables are used to track changes in  /add_word input "word"
    let current_text, previous_text = $("#id_word").val();

    // every 2 seconds check if there is any difference in "word" input of "add_word" form
    setInterval(function(){
        let current_text = $("#id_word").val();

//        if "word" was changed try to translate it
        if (current_text != previous_text) {
            translate_the_text(csrf_token, current_text, studying_lang=sl_short);
            previous_text = current_text;
        }
    }, 2000);
});
