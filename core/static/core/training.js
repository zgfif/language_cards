// event listener that shows and hides
function toggleVisibilityOfCard() {
    const training_div = document.getElementById('trainingBlock')

    classes = training_div.classList

    if (classes.contains('hiddenDiv')) {
        classes.remove('hiddenDiv')
        classes.add('shownDiv')
    } else {
        classes.remove('shownDiv')
        classes.add('hiddenDiv')
    }
}


// function to check if translated is equal to entered word
function checkTranslation() {
    const translation = document.querySelector('#translated span').textContent;

    const entered = document.getElementById('guess').value;

    if (translation == entered) {
        console.log('Correct');
    } else {
        console.log('Incorrect');
    }
}

// event that run checking translation
const check_button = document.getElementById('checkButton');
check_button.addEventListener("click", checkTranslation, false);


// event that shows and hides the "start training" button
const start_button = document.getElementById('startTrainingButton');
start_button.addEventListener('click', toggleVisibilityOfCard, false);

