function addSong(id) {
    let p_id = document.getElementById(`playlist_id`).value
    let name = document.getElementById(`name_${id}`).value
    let artist = document.getElementById(`artist_${id}`).value
    let art = document.getElementById(`art_${id}`).value
    let spotify_id = document.getElementById(`spotifyid_${id}`).value
    let duration = document.getElementById(`duration_${id}`).value

    $.ajax({
        url: "/add_song",
        type: "POST",
        data: { "id": id, "playlist_id": p_id, "name": name, 
            "duration": duration, "artist": artist, "art": art, 
            "spotify_id": spotify_id, csrfmiddlewaretoken: getCSRFToken() },
        dataType : "json",
        success: updateSearch,
        error: updateError
    });
}

function removeSong(id) {
    let p_id = document.getElementById(`playlist_id`).value
    let spotify_id = document.getElementById(`spotifyid_${id}`).value

    $.ajax({
        url: "/remove_song",
        type: "POST",
        data: { "id": id, "playlist_id": p_id, "spotify_id": spotify_id,
            csrfmiddlewaretoken: getCSRFToken() },
        dataType : "json",
        success: updateSearch,
        error: updateError
    });
}

// function updatePage(response) {
//     if (Array.isArray(response)) {
//         updateList(response)
//     } else if (response.hasOwnProperty('error')) {
//         displayError(response.error)
//     } else {
//         displayError(response)
//     }
// }
        
function updateSearch(item) {
    button = document.getElementById(`button_${item.song_id}`);
    if (item.is_added) {
        button.onclick = function () { removeSong(item.song_id); };
        button.innerHTML = `Remove song`;
    }
    else {
        button.onclick = function () { addSong(item.song_id); };
        button.innerHTML = `Add song`;
    }
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}


function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown";
}

function updateError(xhr, status, error) {
    displayError('Status=' + xhr.status + ' (' + error + ')')
}

function displayError(message) {
    $("#error").html(message);
}

function addComment(uuid) {
    let itemTextValue = document.getElementById(`comment_text`).value
    let nameValue = document.getElementById(`comment_name`).value
    $.ajax({
        url: "/add_comment",
        type: "POST",
        data: { "comment_name": nameValue, "comment_text": itemTextValue, "uuid": uuid, csrfmiddlewaretoken: getCSRFToken() },
        dataType : "json",
        success: updateComments,
        error: updateError
    });
}

function getComments(uuid) {
    $.ajax({
        url: `/get_comments/${uuid}`,
	type: "POST",
	data: {csrfmiddlewaretoken: getCSRFToken()},
        dataType : "json",
        success: updateComments,
        error: updateError
    });
}


function updateComments(items) {
    // Adds each new todolist item to the list (only if it's not already here)
    $(items).each(function() {
        let my_id = `id_comment_${this.id}`
        if (document.getElementById(my_id) == null) {
            let comment = document.createElement("div")
            comment.id = my_id
            comment.class = 'col-12'
            let d = new Date(this.date)

            comment.innerHTML = `<div>` + `<span id="id_comment_text_${this.id}">` + sanitize(this.text) + '</span> - ' +
                                `<span id="id_comment_name_${this.id}">` + sanitize(this.name) + '</span> - ' +
                                `<span id="id_comment_date_time_${this.id}">` + d.toLocaleDateString() + ' ' +
                                d.toLocaleTimeString([], {hour: 'numeric', minute: 'numeric'}) + '</span>' + `</div>`
            $('#comments').prepend(comment)
        }
    })
}

// function getList() {
//     $.ajax({
//         url: "update_search",
//         dataType : "json",
//         success: updatePage,
//         error: updateError
//     });
// }

// // Call getList() as soon as page is finished loading to display the to do list
// window.onload = getList;

// // ... also call getList every 5 seconds hereafter to update the list
// window.setInterval(getList, 5000);
