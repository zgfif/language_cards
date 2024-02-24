// this function makes the btn enabled
function enableBtn(btn) {
   btn.attr("disabled", false);
};


// this function makes the btn disabled
function disableBtn(btn) {
    btn.attr("disabled", true);
};


// assign event when the page is fully downloaded
$(document).ready(function() {
    const word = $('#id_word'),
          translation = $('#id_translation'),
          sentence = $('#id_sentence'),
          update_btn = $('#update_button');

    const initWordValue = word.val(),
          initTranslationValue = translation.val(),
          initSentenceValue = sentence.val();

    // by default, "update" button is inactive
   disableBtn(update_btn);

   var changed_inputs = [false, false, false];

    //  this event listener compares the initial value of "input_node" with its changed value
    word.on( "input", function() {
        new_value =$(this).val();

        if (new_value == initWordValue) {
            changed_inputs[0] = false
        } else {
            changed_inputs[0] = true
        }

        if (changed_inputs[0] || changed_inputs[1] || changed_inputs[2]) {
            enableBtn(update_btn);
        } else {
            disableBtn(update_btn);
        }
    });

    translation.on( "input", function() {
        new_value =$(this).val();

        if (new_value == initTranslationValue) {
            changed_inputs[1] = false
        } else {
            changed_inputs[1] = true
        }

        if (changed_inputs[0] || changed_inputs[1] || changed_inputs[2]) {
            enableBtn(update_btn);
        } else {
            disableBtn(update_btn);
        }
    });

    sentence.on( "input", function() {
        new_value =$(this).val();

        if (new_value == initSentenceValue) {
            changed_inputs[2] = false
        } else {
            changed_inputs[2] = true
        }

        if (changed_inputs[0] || changed_inputs[1] || changed_inputs[2]) {
            enableBtn(update_btn);
        } else {
            disableBtn(update_btn);
        }
    });
});

