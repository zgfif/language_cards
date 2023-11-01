const entered_word = document.querySelector('#guess');
const correct_word = document.querySelector('#translated span').textContent;
const check_button = document.querySelector('#checkButton');
const direction = document.querySelector('#direction').dataset.direction;
const id = document.querySelector('#direction').dataset.id;
const csrf_token = document.querySelector('input[name="csrfmiddlewaretoken"]').getAttribute('value')


check_button.addEventListener('click', function () {
    let message = 'Sorry. It is incorrect :('

    let correctness = false

    if (entered_word.value == correct_word) {
        message = 'It is correct!!!';
        show_sentence_example();

        correctness = true

        show_audio();


    }
    update_word(direction, id, correctness);

    show_message(message);
}, false);


function show_message(text='') {
    const message_div = document.querySelector('#wordResult');
    message_div.textContent = text;
}


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
        console.log(audio);
    }
}


// make a post request to update info related to word
function update_word(direction, id, correctness) {
    console.log(window.location.href);

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