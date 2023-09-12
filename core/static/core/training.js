const entered_word = document.querySelector('#guess');
const correct_word = document.querySelector('#translated span').textContent;
const check_button = document.querySelector('#checkButton');

check_button.addEventListener('click', function () {
    let message = 'Sorry. It is incorrect :('

    if (entered_word.value == correct_word) {
        message = 'It is correct!!!';
        show_sentence_example();
        show_audio();
    }

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
