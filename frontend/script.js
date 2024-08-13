$(document).ready(() => {
    $("#linkform").on("submit", (e) => {
        e.preventDefault();
        $('#recommendations').children().remove();

        const searchdata =  $("#textinput").val()

        $.ajax({
            url: 'http://localhost:8040/predict',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                text: searchdata
            }),
            success: (response) => { //use foreach from courses, can just start by outputting links (like how it does now)
                $
                console.log(response)
                $('<h4>').text('results:').appendTo('#recommendations');
                $('<p>').text(response).appendTo('#recommendations');
            },
            error: (xhr, status, error) => {
                console.log(error)
                $('<p>').text(error).appendTo('#recommendations');
            }
        });
    })  

})