async function init_model(model_name) {
    $.ajax({
        url: 'http://localhost:8040/init_model',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            model_name: model_name
        }),
        success: (response) => {
            console.log(response.message);
        },
        error: (xhr, status, error) => {
            throw new Error(`Error: ${error}, Status: ${status}`)
        }
    });
}

async function does_model_exist(model_name) {
    $.ajax({
        url: 'http://localhost:8040/model_exists',
        method: 'GET',
        contentType: 'application/json',
        data: JSON.stringify({
            model_name: model_name
        }),
        success: (response) => {
            console.log(response.message);
            return response.exists
        },
        error: (xhr, status, error) => {
            throw new Error(`Error: ${error}, Status: ${status}`)
        }
    });
}

async function is_model_trained(model_name) {
    $.ajax({
        url: 'http://localhost:8040/model_trained',
        method: 'GET',
        contentType: 'application/json',
        data: JSON.stringify({
            model_name: model_name
        }),
        success: (response) => {
            console.log(response.message);
            return response.trained
        },
        error: (xhr, status, error) => {
            throw new Error(`Error: ${error}, Status: ${status}`)
        }
    });
}

async function send_training_examples(positive_examples, negative_examples) {
    const model_name = localStorage.getItem("model_name")
    $.ajax({
        url: 'http://localhost:8040/train',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            positive_examples: positive_examples,
            negative_examples: negative_examples,
            model_name: model_name
        }),
        success: (response) => {
            console.log(response.message);
        },
        error: (xhr, status, error) => {
            throw new Error(`Error: ${error}, Status: ${status}`)
        }
    });
}

// async function get_rec() {
//     const model_name = localStorage.getItem("model_name")
//     $.ajax({
//         url: 'http://localhost:8040/rec',
//         method: 'GET',
//         contentType: 'application/json',
//         success: (response) => {
//             return response.rec; // for now, just a link
//         },
//         error: (xhr, status, error) => {
//             console.log(error);
//             $('<p>').text(error).appendTo('#recs');
//         }
//     });
//     return
// }













$(document).ready(() => {
    if (localStorage.getItem("model_name") != null) {
        $('#model-chosen').css("display", "block");
        $('#model-not-chosen').css("display", "none");
    } else {
        $('#model-not-chosen').css("display", "block");
        $('#model-chosen').css("display", "none");
    }

    $("#existing-model-form").on("submit", (e) => {
        e.preventDefault();
        const model_name = $("#existing-model-input").val();
        const model_exists = does_model_exist(model_name)
        if (model_exists) {
            localStorage.setItem("model_name", model_name)
        } else {
            console.log('model does not exist with that name')
        }
    });

    $("#new-model-form").on("submit", (e) => {
        e.preventDefault();
        const model_name = $("#existing-model-input").val();
        const model_exists = does_model_exist(model_name)
        if (model_exists) {
            console.log('model already exists with that name')
        } else {
            init_model(model_name)
        }
    });

    $("#end-model-session").on("click", (e) => {
        e.preventDefault();
        localStorage.clear();
    });


    $("#add-new-examples").on("click", (e) => {
        e.preventDefault();
        $("#input-data").css('display', 'block');
        $("#recommendations").css('display', 'none');
    });

    $("#show-recommendations").on("click", (e) => {
        e.preventDefault();
        const model_name = localStorage.get("model_name")
        let is_model_trained
        try {
            is_model_trained = is_model_trained(model_name)
            if (is_model_trained) {
                $("#recommendations").css('display', 'block');
                $("#input-data").css('display', 'none');
            } else {
                console.log('error: need to train the model before you get recommendations')
            }
        } catch (error) {
            console.log(error)
        }
    });

    $("#song-form").on("submit", (e) => {
        e.preventDefault();
        const positive_examples = $("#positive-examples-input").val();
        const negative_examples = $("#negative-examples-input").val();
        try {
            send_training_examples(positive_examples, negative_examples)
        } catch (error) {
            console.log(error)
        }
    });

    // $("#newrec").on("click", (e) => {
    //     e.preventDefault();
    //     try {
    //         rec = get_rec();
    //     } catch (error) {
    //         console.log(error)
    //     }
    // });

    // $("#classify-good").on("click", (e) => {
    //     e.preventDefault();
    //     curr_uri = div.id
    //     send_training_examples(curr_uri, "")
    // });

    // $("#classify-bad").on("click", (e) => {
    //     e.preventDefault();
    //     curr_uri = div.id
    //     const user_id = localStorage.getItem("", curr_uri)

    // });
});





