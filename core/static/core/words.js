document.addEventListener("DOMContentLoaded", (event) => {
    // assign the Authorization Token to variable for further use in "get_words_from_api" function
    const authorization_token = auth_token();


    // make request on 'api/words' with Authorization Token to retrieve the list of words
    get_words_from_api(url = 'api/words', auth_token = authorization_token);


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


    $('#searchInput').on('input', function(event) {
        clear_table()

        let value = $(this).val();

        if (value) {
            setTimeout(get_words_from_api(url = `/api/words/?q=${value}`, auth_token = authorization_token), 500)
        } else {
            setTimeout(get_words_from_api(url = '/api/words/', auth_token = authorization_token), 500)
        }
    });
});


// declaration of functions is below


// this function is used to retrieve data from /api/words using Authorization token
function get_words_from_api(url, auth_token) {
    $.get({
    url: url,
    headers: { 'Authorization': `Token ${auth_token}` }
    }, function(data, status) {
        if (status == 'success'){
           const results = data['results'];

            fill_table_with_data(results);

            const next_url = data['next'];

            if (next_url) {
                $('#moreWordsButton').attr("style", "display:block");
                 $('#moreWordsButton').click(function(){
                    get_words_from_api(url = next_url, auth_token = auth_token);
                 });
            } else {
                $('#moreWordsButton').attr("style", "display:none");
            }
        } else {
            console.log('something went wrong');
        }
    }, 'json')
}


// this function is used to retrieve Authorization token from element with 'data-auth-token' attribute
function auth_token() {
    const auth_node = document.querySelector('[data-auth-token]');
   if (auth_node) {
        return auth_node.getAttribute('data-auth-token');
   } else {
        return null
   }
}


// this function appends a new row to table the row has 10 cells with data retrieved form results
function fill_table_with_data(results = false) {
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
                                                ${image_badge_tag(ru_en = word['ru_en'], en_ru = word['en_ru'])}
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

                    second_cell.setAttribute('style', 'vertical-align: middle')
            }
        }
    }
}


// this function builds the image tag whose image name depending on boolean values of "en_ru" and "ru_en"
// example of return: <img src="/static/core/images/false_true.svg" alt="progress" style="height:20px">
function image_badge_tag(ru_en = false, en_ru = false) {
    let img_name = 'false_false.svg';

    if (ru_en && en_ru) {
        img_name = 'true_true.svg';
    } else if (ru_en && !en_ru) {
        img_name = 'true_false.svg';
    } else if (!ru_en && en_ru) {
        img_name = 'false_true.svg';
    }

    return `<img src="/static/core/images/${img_name}" alt="progress" style="margin: 0 10px;height:20px">`
}


// this function removes all rows from table
function clear_table() {
    $('#tableBody').children('tr').remove();
}

