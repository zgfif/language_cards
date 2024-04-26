document.addEventListener("DOMContentLoaded", (event) => {
    // assign Authorization Token to variable for further use in "get_words_from_api" function
    const authorization_token = auth_token();


    // make request on 'api/words' with Authorization Token to retrieve the list of words
    get_words_from_api(url = 'api/words', auth_token = authorization_token);


    // after clicking "delete" appears the confirmation dialog "Are you sure want to delete ...?"
    $(document).on('click', '.delWordBtn', function(event) {
        message = `Are you sure want to delete "${$(event.target).attr('data-word')}"?`
        return confirm(message);
    });
});


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

         for (let word of results) {
            let row = table_body.insertRow(-1);
            const cell1 = row.insertCell(0);
            const cell2 = row.insertCell(1);
            const cell3 = row.insertCell(2);
            const cell4 = row.insertCell(3);
            const cell5 = row.insertCell(4);
            const cell6 = row.insertCell(5);
            const cell7 = row.insertCell(6);
            const cell8 = row.insertCell(7);
            const cell9 = row.insertCell(8);
            const cell10 = row.insertCell(9);

            cell1.innerHTML = `<b>${word['word']}</b>`;
            cell2.innerHTML = word['translation'];
            cell3.innerHTML = word['sentence'];
            cell4.innerHTML = image_tag(word['en_ru'], 'yes.svg', 'no.svg')
            cell5.innerHTML = image_tag(word['ru_en'], 'yes.svg', 'no.svg')
            cell6.innerHTML = image_tag(word['is_known'], 'bold_yes.svg', 'no.svg')
            cell7.innerHTML = `<audio controls src="${word['full_audio_path']}"></audio>`;
            cell8.innerHTML = `<a class="delWordBtn" data-word="${word['word']}" href="/words/${word['id']}/delete">delete</a>`;
            cell9.innerHTML = `<a href="/words/${word['id']}/edit">edit</a>`;
            cell10.innerHTML = `<a href="/words/${word['id']}/reset">reset progress</a>`;
        }
    }
}


// this function builds the image tag whose image name depends on value
function image_tag(boolean_val, when_true, when_false) {
    let img_name = when_false;

    if (boolean_val) {img_name = when_true }

    return `<img src="/static/core/images/${img_name}" alt="${boolean_val}" style="height:20px">`
}
