const entered_word = document.querySelector('#guess');
const correct_word = document.querySelector('#translated span').textContent;
const check_button = document.querySelector('#checkButton');
const direction = document.querySelector('#direction').dataset.direction;
const en_word = document.querySelector('#direction').dataset.en_word;
const id = document.querySelector('#direction').dataset.id;
const csrf_token = document.querySelector('input[name="csrfmiddlewaretoken"]').getAttribute('value');
const sentence_element = document.querySelector('#sentence span');
const next_button = document.querySelector('#nextButton');
const finish_button = document.querySelector('#finishButton');


// if the sentence has learning word inside it, make it bold
decorate_sentence(sentence_element, en_word);

// put cursor inside the input
entered_word.select();


// checks the word after clicking Enter
entered_word.addEventListener('keypress', function(event) {
    if (event.keyCode == 13) {
        check_button.click();
    }
});

// the page has the "finish" after clicking on it opens "confirm"
if (finish_button) {
    finish_button.addEventListener('click', function() {
     confirm("Congratulations! You've finished the test");
});
} else {
    console.log('no finish button');
}



// this event listener tracks the the "check button" and validates entered word
check_button.addEventListener('click', function () {
    let message = 'It is incorrect :('

    let correctness = false

    //    clause is the entered word is CORRECT
    if (process_text(entered_word.value) == process_text(correct_word)) {
        message = 'It is correct!';

        show_sentence_example();

        correctness = true

        show_audio();

        //  if we have "next" button focus on the "next" button, else - focus on "finish" button
        if (next_button) { next_button.focus(); } else { finish_button.focus(); }
    }

    // update knowledge about this word
    update_word(direction, id, correctness);

    show_message(message, correctness);
}, false);


// shows message if the word is correct or incorrect
function show_message(text='', correctness=false) {
    const message_div = document.querySelector('#wordResult');
    message_div.textContent = text;

    if (correctness == true) {
       make_text_green(message_div);
    } else {
       make_text_red(message_div);
    }
}


// shows the example of text with the word which the user trying to learn
function show_sentence_example() {
    const sentence_div = document.querySelector('#sentence');
    sentence_div.classList.remove('hiddenDiv');
    sentence_div.classList.add('shownDiv');
}


// show and play audio for ru-eng
function show_audio() {
    audio_div = document.querySelector('#en_audio');
    if (audio_div) {
        audio_div.classList.remove('hiddenDiv');
        audio = audio_div.querySelector('audio');
        audio.play()
//        console.log(audio);
    }
}


// make a post request to update info related to word
function update_word(direction, id, correctness) {
//    console.log(window.location.href);

    fetch(window.location.href, {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
         'X-CSRFToken': csrf_token,

    },
    body: JSON.stringify({ "id": id, "direction": direction, 'correctness': correctness})
})
   .then(response => response.json())
//   .then(response => console.log(JSON.stringify(response)))
}


// makes text of the element red
function make_text_red(element) {
    element.classList.add('redText');
    element.classList.remove('greenText');
}


// makes text of the element green
function make_text_green(element) {
    element.classList.remove('redText');
    element.classList.add('greenText');
}


// adds bold tag around each word in the text
function make_word_bold(text='', word='') {
    modified_word = clear_articles(word)
    return text.replaceAll(word, '<b>' + word + '</b>')
}


// modifies text of the element if it has the word
function decorate_sentence(element, word='') {
    element.innerHTML = make_word_bold(element.textContent, clear_articles(word))
}


// removes articles ("a ", "an ", "the ") and infinitive ("to ") and returns the word
function clear_articles(word) {
    reg2 = /^(to\s|a\s|an\s|the\s)/
    return word.replace(reg2, '')
}

// return any text in lower case
function make_lower_case(text='') {
    return text.toLowerCase()
}

// returns the text where 2 or more spaces in a row are replaced with only 1 space
function remove_excess_spaces(text='') {
    reg = /\s{2,}/g;
    return text.replace(reg, ' ').trim();
}

// returns text in lower case and without multiple spaces in a row
function process_text(text='') {
    const lower_case = make_lower_case(text)
    return remove_excess_spaces(lower_case)
}

