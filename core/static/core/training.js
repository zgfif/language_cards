//show html element
function showHtmlElement(element) {
    element.classList.remove('hiddenDiv')
    element.classList.add('shownDiv')
}

//hide html element
function hideHtmlElement(element) {
    element.classList.add('hiddenDiv')
    element.classList.remove('shownDiv')
}


// toggle visibility of element
function toggleVisibilityOfCard() {
    const card = document.getElementById('trainingBlock')
    const classes = card.classList

    if (classes.contains('hiddenDiv')) {
        showHtmlElement(card)
    } else {
        hideHtmlElement(card)
    }
}


// function to check if translated is equal to entered word
function checkTranslation() {
    const translation = document.querySelector('#translated span').textContent;
    showHtmlElement(document.querySelector('#translated'))

    const entered = document.getElementById('guess').value;

    if (translation == entered) {
        console.log('Correct');


    } else {
        console.log('Incorrect');
    }
    document.getElementById('guess').value = '';
    showNextCard();
}

// event that run checking translation
const check_button = document.getElementById('checkButton');
check_button.addEventListener("click", checkTranslation, false);


// event that shows and hides the "start training" button
const start_button = document.getElementById('startTrainingButton');
const training_div = document.getElementById('trainingBlock')
start_button.addEventListener('click', toggleVisibilityOfCard, false);



// return the list of learning words
function retrieveWords() {
    const cards_data = document.getElementById('wordsdata').textContent;
    return Array(JSON.parse(cards_data))[0]
}

// fill the card with information
function fillCard(know, dontKnow) {
    document.querySelector('#word span').textContent = know;
    document.querySelector('#translated span').textContent = dontKnow;
}

fillCard('стол', 'table')
