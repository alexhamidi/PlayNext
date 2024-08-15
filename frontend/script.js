$(document).ready(() => {
    $("#linkform").on("submit", (e) => {
        e.preventDefault();
        $('#recommendations').children().remove();

        const gooddata =  $("#goodtextinput").val()
        const baddata =  $("#badtextinput").val()

        $.ajax({
            url: 'http://localhost:8040/predict',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                gooddata: gooddata,
                baddata: baddata
            }),
            success: (response) => { //use foreach from courses, can just start by outputting links (like how it does now)
                
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