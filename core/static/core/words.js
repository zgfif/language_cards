document.addEventListener("DOMContentLoaded", (event) => {
    // assign the Authorization Token to variable for further use in "get_words_from_api" function
    const authorization_token = getAuthToken();



    // after clicking "delete" appears the confirmation dialog "Are you sure want to delete ...?"
    $(document).on('click', '.delWordBtn', function(event) {
        message = `Are you sure want to delete "${$(event.target).attr('data-word')}"?`
        return confirm(message);
    });

    // play audio pronunciation after clicking on "play" button
    $(document).on('click', '.playBtn', function(event) {
        play_element = $(event.target.parentNode).find('.audioTag');
        play_element[0].play();
    });


    make_request_to_server_and_fill_table(url = 'api/words', auth_token = authorization_token, is_cleared_table = true);

    enableSearching(auth_token = authorization_token)
});


// declaration of functions is below



// this function is used to retrieve Authorization token from element with 'data-auth-token' attribute
function getAuthToken() {
    const auth_node = document.querySelector('[data-auth-token]');
   if (auth_node) {
        return auth_node.getAttribute('data-auth-token');
   } else {
        return null
   }
}


// this function appends a new row to table the row has 10 cells with data retrieved form results
function fill_table_with_data(results = false, is_cleared_table = true) {
    if (is_cleared_table) {
    	clear_table();
    }

    if (results) {
        const table_body = document.getElementById("tableBody");
        if (table_body) {
           // we iterate over our the word's list [{'word': , 'translation':, 'sentence': ,..}, {}, ..., {}]
           for (let word of results) {
                // add a new row in the end of existing table (this row will contain word, translation, sentence, etc)
                let main_row = table_body.insertRow(-1);

		    // inside the new word's row a new cell
                    first_cell = main_row.insertCell(0);

                    // as any cells haven't method "insertRow" we have to create a new "inner" table
                    inner_table = document.createElement('table');

                    // insert "inner" table into "main" cell
                    first_cell.appendChild(inner_table);

                    // insert 3 rows into the "inner" table
                    inner_row1 = inner_table.insertRow(0) // row for "word", audio tag and badge (two rectangles)
                    inner_row2 = inner_table.insertRow(1) // row for "translation"
                    inner_row3 = inner_table.insertRow(2) // row for "sentence"

                    // row contains 'cat', 'cat' audio tag and two "progress" rectangles
                    // (depends on boolean ru_en and en_ru) "green" is true, "white" is false
                    inner_row1.innerHTML = `<div class="word_and_audio_div">
                                                <img class="playBtn" src="/static/core/images/play.svg" height="20px" alt="play button">
                                                ${image_badge_tag(know_native_to_studying = word['know_native_to_studying'], know_studying_to_native = word['know_studying_to_native'])}
                                                <b style="padding-right:15px;">${word['word']}</b>
                                                <audio class="audioTag" style="padding-right:15px;" controls src="${word['full_audio_path']}" hidden></audio>
                                            </div>`;

                    // "кошка" translation
                    inner_row2.innerHTML = word['translation'];

                    // sentence, for example: "It's very difficult to find black cat in black room."
                    inner_row3.innerHTML =  word['sentence'];

                    // add new cell to "main" row for dropdown menu (three dots sign)
                    second_cell = main_row.insertCell(1)

                    // this "second" cell in the "main" row contains menu:
                    // 1 menu item: update
                    // 2 menu item: reset progress (make en_ru false, and ru_en false again)
                    // 3 menu item: delete word from user's vocabulary
                    second_cell.innerHTML = `
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

                    second_cell.setAttribute('style', 'vertical-align: middle');

            }
        } 
    }
    
}


// this function builds the image tag whose image name depending on boolean values of "en_ru" and "ru_en"
// example of return: <img src="/static/core/images/false_true.svg" alt="progress" style="height:20px">
function image_badge_tag(know_native_to_studying = false, know_studying_to_native = false) {
    let img_name = 'false_false.svg';

    if (know_native_to_studying && know_studying_to_native) {
        img_name = 'true_true.svg';
    } else if (know_native_to_studying && !know_studying_to_native) {
        img_name = 'true_false.svg';
    } else if (!know_native_to_studying && know_studying_to_native) {
        img_name = 'false_true.svg';
    }

    return `<img src="/static/core/images/${img_name}" alt="progress" style="margin: 0 10px;height:20px">`
}


// this function removes all rows from table
function clear_table() {
    $('#tableBody').children('tr').remove();
}


// this function validates if string has only spaces without any other symbols
function has_only_spaces(str = "") {
   let result = false

   if (str.length > 0) {
        const str_without_spaces = str.replace(/\s+/g, '');

        if (str_without_spaces.length == 0) { result = true }
   }

   return result
};


// before showing results we should clear nothing found rows
function clear_nothing_found_rows() {
    document.querySelectorAll(".noResultsBody").forEach((element) => element.remove());

}


function toggle_next_button(next_url=false) {
    if (next_url) {
	let is_cleared_table = false;
	
        $('#moreWordsButton').show(500);
        
	$('#moreWordsButton').one('click', function() {
            make_request_to_server_and_fill_table(url = next_url, auth_token = auth_token, is_cleared_table = is_cleared_table);
	});
    } else {
        $('#moreWordsButton').hide(500);
    }
};


async function fetchData(url = 'api/words', auth_token = null) {
    const headers = new Headers({ 'Authorization': `Token ${auth_token}`, });

    const response = await fetch(url, { headers: headers });

    const data = await response.json();

    return data;
}


async function make_request_to_server_and_fill_table(url, auth_token, is_cleared_table = true) {
    const data = await fetchData(url, auth_token);

    fill_table_with_data(data['results'], is_cleared_table = is_cleared_table);

    toggle_next_button(data['next']);
}

// this function is used to enable searching
function enableSearching(auth_token = null) {
    const searchInput = $('#searchInput');
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
        make_request_to_server_and_fill_table(url = `/api/words/?q=${value}`, 
					      auth_token = auth_token, 
		                              is_cleared_table = true);
    }

/*    let timer = '';

    // each time user presses any key in search input we make request to search by value of input
    $('#searchInput').keyup(function() {
      clearTimeout(timer);

      timer = setTimeout(function() {
        let value = $('#searchInput').val()

        if (!has_only_spaces(value)) {
            // making request to retrieve results of searching
            make_request_to_server_and_fill_table(url = `/api/words/?q=${value}`, auth_token = auth_token, is_cleared_table = true)

            // we wait 200 milliseconds to count row results
           setTimeout(() => {
                 // count founded words
                let count_of_rows = $("#tableBody > tr").length;
                add_nothing_found_row(value, count_of_rows);
           }, 200);
        }

      }, 1000); // Waits for 1 second after last keyup to execute the above lines of code
    });
*/
};


// this function is used to add row with "Nothing found with ..." to table body
function add_nothing_found_row(query = '', count = 0) {
    if (count == 0) {
        $("#tableBody").append(`<tr><td style="align-text:center">
        Nothing found with <b>"${query}"</b></td></tr>`);
    }
};
