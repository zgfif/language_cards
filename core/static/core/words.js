document.addEventListener("DOMContentLoaded", (event) => {

    // after clicking "delete" appears the confirmation dialog "Are you sure want to delete ...?"
    $(document).on('click', '.delWordBtn', function(event) {
        message = `Are you sure want to delete "${$(event.target).attr('data-word')}"?`
        return confirm(message);
    });


    // play audio word pronunciation after clicking on "play" button
    $(document).on('click', '.playBtn', function(event) {
        playElement = $(event.target.parentNode).find('.audioTag');
        playElement[0].play();
    });

    // play audio sentence pronunciation after clicking on "play" button
    $(document).on('click', '.playBtnSentence', function(event) {
        playElement = $(event.target.parentNode).find('.audioTag');
        playElement[0].play();
    });

    makeRequestToServerAndFillTable(url = 'api/words', 
	                            authToken = getAuthToken(), 
	                            performClearingTable = true);


    enableSearching(authToken = getAuthToken());

});


// Declaration of functions is below:


// this function is used to retrieve Authorization token from element with 'data-auth-token' attribute
function getAuthToken() {
    const authNode = document.querySelector('[data-auth-token]');
    if (authNode) {
        return authNode.getAttribute('data-auth-token');
    } else {
        return null;
    }
};


// this function appends a new row to table the row has 10 cells with data retrieved form results
function fillTableWithData(results = false, performClearingTable = true) {
    if (performClearingTable) { 
        clearTable(); 
    }

    if (results) {

        const tableBody = document.getElementById("tableBody");
        
	if (tableBody) {
           // we iterate over our the word's list [{'word': , 'translation':, 'sentence': ,..}, {}, ..., {}]
           for (let word of results) {
                // add a new row in the end of existing table (this row will contain word, translation, sentence, etc)
                let mainRow = tableBody.insertRow(-1);

		    // inside the new word's row a new cell
                    firstCell = mainRow.insertCell(0);

                    // as any cells haven't method "insertRow" we have to create a new "inner" table
                    innerTable = document.createElement('table');

                    // insert "inner" table into "main" cell
                    firstCell.appendChild(innerTable);

                    // insert 3 rows into the "inner" table
                    innerRow1 = innerTable.insertRow(0) // row for "word", audio tag and badge (two rectangles)
                    innerRow2 = innerTable.insertRow(1) // row for "translation"
                    innerRow3 = innerTable.insertRow(2) // row for "sentence"

                    // row contains 'cat', 'cat' audio tag and two "progress" rectangles
                    // (depends on boolean ru_en and en_ru) "green" is true, "white" is false
                    innerRow1.innerHTML = `<div class="word_and_audio_div">
                                                <img class="playBtn" 
						     src="/static/core/images/play.svg" 
						     height="20px" alt="play button">
                                                ${imageBadgeTag(knowNativeToStudying = word['know_native_to_studying'], 
						                knowStudyingToNative = word['know_studying_to_native'])}
                                                <b style="padding-right:15px;">${word['word']}</b>
                                                
						<audio class="audioTag" 
						       style="padding-right:15px;" 
						       controls 
						       src="${word['full_audio_word_path']}" 
						       hidden>
						</audio>
                                            </div>`;

                    // "кошка" translation
                    innerRow2.innerHTML = word['translation'];

                    // sentence, for example: "It's very difficult to find black cat in black room."
		    if (word['full_audio_sentence_path']) {
                    	innerRow3.innerHTML = `<span><img class="playBtnSentence" 
						     src="/static/core/images/play.svg" 
						     height="20px" alt="play button">
						     ${word['sentence']}
						     <audio class="audioTag" 
						           style="padding-right:15px;" 
						           controls 
						           src="${word['full_audio_sentence_path']}" hidden>
						     </audio>
				    		</span>
						
				    `;

		    } else {
                    	innerRow3.innerHTML =  word['sentence'];
		    }

                    // add new cell to "main" row for dropdown menu (three dots sign)
                    secondCell = mainRow.insertCell(1)

                    // this "second" cell in the "main" row contains menu:
                    // 1 menu item: update
                    // 2 menu item: reset progress (make en_ru false, and ru_en false again)
                    // 3 menu item: delete word from user's vocabulary
                    secondCell.innerHTML = `
                                    <div class="dropdown">
                                      <img src="/static/core/images/three_v_dots.svg" class="dropdown-toggle"
                                            data-bs-toggle="dropdown" aria-expanded="true" alt="three_dots"
                                            style="height:20px">
                                      <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="/words/${word['id']}/edit">update</a></li>
                                        <li><a class="dropdown-item" href="/words/${word['id']}/reset">
                                            reset progress
                                            </a>
                                        </li>
                                        <li>
                                            <a class="delWordBtn dropdown-item" data-word="${word['word']}"
                                            style="color:red" href="/words/${word['id']}/delete">
                                                delete
                                            </a>
                                        </li>
                                      </ul>
                                    </div>`

                    secondCell.setAttribute('style', 'vertical-align: middle');

            }
        } 
    }
    
}


// this function builds the image tag whose image name depending on boolean values of "en_ru" and "ru_en"
// example of return: <img src="/static/core/images/false_true.svg" alt="progress" style="height:20px">
function imageBadgeTag(knowNativeToStudying = false, knowStudyingToNative = false) {
    let imgName = 'false_false.svg';

    if (knowNativeToStudying && knowStudyingToNative) {
        imgName = 'true_true.svg';
    } else if (knowNativeToStudying && !knowStudyingToNative) {
        imgName = 'true_false.svg';
    } else if (!knowNativeToStudying && knowStudyingToNative) {
        imgName = 'false_true.svg';
    }

    return `<img src="/static/core/images/${imgName}" alt="progress" style="margin: 0 10px;height:20px">`
}


// this function removes all rows from table
function clearTable() {
    $('#tableBody').children('tr').remove();
}


// this function validates if string has only spaces without any other symbols
function hasOnlySpaces(str = "") {
   let result = false

   if (str.length > 0) {
        const strWithoutSpaces = str.replace(/\s+/g, '');

        if (strWithoutSpaces.length == 0) { result = true }
   }

   return result
};


// before showing results we should clear nothing found rows
function clearNothingFoundRows() {
    document.querySelectorAll(".noResultsBody").forEach((element) => element.remove());

}


function toggleMoreButton(nextUrl=false) {
    $('#moreWordsButton').remove();

    if (nextUrl) {
	const clearTable = false;
        //  if we have nextUrl we create "more" button 
        $('#moreWordsDiv').append('<button class="btn" type="button" id="moreWordsButton">more</button>');
        // attach on this button eventlistener to load more words
	$('#moreWordsButton').one('click', function() {
            makeRequestToServerAndFillTable(url = nextUrl, 
		                            authToken = authToken, 
		                            performClearingTable = clearTable);
	});
    } 
};


async function fetchData(url = 'api/words', authToken = null) {
    const headers = new Headers({ 'Authorization': `Token ${authToken}`, });

    const response = await fetch(url, { headers: headers });

    const data = await response.json();

    return data;
}


async function makeRequestToServerAndFillTable(url, authToken, performClearingTable = true) {
    const data = await fetchData(url, authToken);

    fillTableWithData(data['results'], performClearingTable = performClearingTable);

    toggleMoreButton(data['next']);
}

// this function is used to enable searching
function enableSearching(authToken = null) {
    const searchInput = $('#searchInput'),
          timeoutInterval = 1000;
    
    let doneTyping;

    searchInput.on('keydown', function () {
        clearTimeout(doneTyping);
    });


    searchInput.on('keyup', function () {
	clearTimeout(doneTyping);
	doneTyping = setTimeout(callback, timeoutInterval);
    });

    function callback() {
        let value = searchInput.val();
        makeRequestToServerAndFillTable(url = `/api/words/?q=${value}`, 
					      authToken = authToken, 
		                              performClearingTable = true);
    }
};


