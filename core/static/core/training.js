console.log('hello from training');

function checkTranslation() {
    const translation = document.getElementById('translated').textContent;

    const entered = document.getElementById('guess').textContent;

    if (translation == entered) {
        console.log('Correct');
    } else {
        console.log('Incorrect');
    }
}

const button = document.getElementById('checkButton');
button.addEventListener("click", checkTranslation, false);
