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

    // retrieving inputs
    const word = $('#id_word'),
          translation = $('#id_translation'),
          sentence = $('#id_sentence'),
          update_btn = $('#update_button');


    // by default, "update" button is inactive
   disableBtn(update_btn);

    // by default, all inputs in the form are not changed. This object is used to persist condition of three inputs:
    // word, translation and sentence.
   var changed_inputs ={ 'word': false, 'translation': false, 'sentence': false }


   function assignInputListener(input_node, input_name) {
        // retrieving default value of the input
        const init_input_value = input_node.val();

        // assign listener on the input will trigger when something changes in the input
        input_node.on( 'input', function() {

            // retrieving the current value of the input
            new_value =$(this).val();

            // if the value of the input node is changed, it will update the condition of this input
            if (new_value == init_input_value) {
                changed_inputs[input_name] = false
            } else {
                changed_inputs[input_name] = true
            }

            // if, at least, one of the input states is changed the button becomes active
            if (changed_inputs['word'] || changed_inputs['translation'] || changed_inputs['sentence']) {
                enableBtn(update_btn);
            } else {
                disableBtn(update_btn);
            }
        });
   }

   assignInputListener(word, 'word');
   assignInputListener(translation, 'translation');
   assignInputListener(sentence, 'sentence');
});
