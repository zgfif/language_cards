// this js file is used in add_word.html

// this event listener is used:
// after submitting the "add word" form the "add" button becomes disabled to prevent a second adding the same word.
$("form").submit(function () {
    $("#add_button").attr("disabled", true);
});
