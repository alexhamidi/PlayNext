$(document).ready(async() => {
//getting the number of training examples will remove the need for a trained chec, everything can be stored in local storage


    /*****************************
    CHECK IF THE MODEL IS CHOSEN
    *****************************/
    const model_name = localStorage.getItem("model_name");
    if (model_name != null) {
        $('#model-chosen').css("display", "block");
        $('#model-name').text(model_name);
        $('#model-not-chosen').css("display", "none");
    } else {
        await load_model_options()
        $('#model-not-chosen').css("display", "block");
        $('#model-chosen').css("display", "none");
    }

    /*****************************
    ADD A NEW MODEL AND SELECT IT
    *****************************/
    $("#new-model-form").on("submit", async (e) => {
        e.preventDefault();
        const model_name = $("#new-model-input").val();
        if (model_name === '') {
            console.log('need to input')
            return;
        }
        try {
            console.log(model_name)
            const model_exists = await does_model_exist(model_name);
            console.log(model_exists);
            if (model_exists) {
                console.log('model already exists with that name');
            } else {
                await init_model(model_name);
                localStorage.setItem("model_name", model_name);
                location.reload()
            }
        } catch (error) {
            console.error(error);
        }
    });

    /*****************************
    TOGGLE NEW EXAMPLES SCREEN
    *****************************/
    $("#add-new-examples").on("click", (e)=> {
        e.preventDefault();
        $("#recs").css('display', 'none');
        $("#input-data").css('display', 'block');
    })

    /*****************************
    TOGGLE REC SCREEN
    *****************************/
    $("#show-recs").on("click", async (e) => {
        e.preventDefault();
        const model_name = localStorage.getItem("model_name");
        try {
            const trained = await is_model_trained(model_name);
            if (trained) {
                $("#recs").css('display', 'block');
                $("#input-data").css('display', 'none');
                // add showing logic
            } else {
                console.log('error: need to train the model before you get recommendations');
            }
        } catch (error) {
            console.error(error);
        }
    });

    /*******************************
    HANDLE SUBMISSION OF TRAIN SONGS
    *******************************/
    $("#song-form").on("submit", async (e) => {
        e.preventDefault();
        const positive_examples = $("#positive-examples-input").val();
        const negative_examples = $("#negative-examples-input").val();
        try {
            await send_training_examples(positive_examples, negative_examples);
        } catch (error) {
            console.error(error);
        }
    });

    $("#end-model-session").on("click", (e) => {
        localStorage.clear();
        location.reload();
    })

});
/*******************************
JS UTILITY FUNCTIONS
*******************************/

async function load_model_options() {
    model_options = await get_all_model_names()
    console.log(model_options)
    if (model_options.length === 0) {
        $('<p>')
        .text('no models exist here (yet)')
        .appendTo('#existing-area')
    } else {
        $('<form>')
            .append(
                $('<select>')
                .attr('id', 'model-select')
                .attr('name', 'model-select')
                .append(
                    $('<option>')
                    .text('select a model')
                    .attr('value', "")
                )
            )
            .appendTo('#existing-area')
        $.each(model_options, (index, option) => {
            console.log(option)
            $('<option>')
            .attr('value', option)
            .text(option)
            .appendTo('#model-select')
        })
    }
}

/*******************************
API REQUESTS
*******************************/

function get_all_model_names() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: 'http://localhost:8040/all_models',
            method: 'GET',
            contentType: 'application/json',
            success: (response) => {
                console.log(response.message);
                resolve(response.model_names);
            },
            error: (xhr, status, error) => {
                let errorMessage;
                try {
                    const errorResponse = JSON.parse(xhr.responseText);
                    errorMessage = errorResponse.detail || error;
                } catch (e) {
                    errorMessage = error;
                }
                reject(new Error(`Error: ${errorMessage}, Status: ${status}`));
            }
        });
    });
}

function init_model(model_name) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: 'http://localhost:8040/init_model',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ model_name: model_name }),
            success: (response) => {
                console.log(response.message);
                resolve(response);
            },
            error: (xhr, status, error) => {
                let errorMessage;
                try {
                    const errorResponse = JSON.parse(xhr.responseText);
                    errorMessage = errorResponse.detail || error;
                } catch (e) {
                    errorMessage = error;
                }
                reject(new Error(`Error: ${errorMessage}, Status: ${status}`));
            }
        });
    });
}

function does_model_exist(model_name) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: 'http://localhost:8040/model_exists',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ model_name: model_name }),
            success: (response) => {
                console.log(response.message);
                resolve(response.exists);
            },
            error: (xhr, status, error) => {
                let errorMessage;
                try {
                    const errorResponse = JSON.parse(xhr.responseText);
                    errorMessage = errorResponse.detail || error;
                } catch (e) {
                    errorMessage = error;
                }
                reject(new Error(`Error: ${errorMessage}, Status: ${status}`));
            }
        });
    });
}

function is_model_trained(model_name) {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: 'http://localhost:8040/model_trained',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ model_name: model_name }),
            success: (response) => {
                console.log(response.message);
                resolve(response.trained);
            },
            error: (xhr, status, error) => {
                let errorMessage;
                try {
                    const errorResponse = JSON.parse(xhr.responseText);
                    errorMessage = errorResponse.detail || error;
                } catch (e) {
                    errorMessage = error;
                }
                reject(new Error(`Error: ${errorMessage}, Status: ${status}`));
            }
        });
    });
}

function send_training_examples(positive_examples, negative_examples) {
    const model_name = localStorage.getItem("model_name");
    return new Promise((resolve, reject) => {
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
                resolve(response);
            },
            error: (xhr, status, error) => {
                let errorMessage;
                try {
                    const errorResponse = JSON.parse(xhr.responseText);
                    errorMessage = errorResponse.detail || error;
                } catch (e) {
                    errorMessage = error;
                }
                reject(new Error(`Error: ${errorMessage}, Status: ${status}`));
            }
        });
    });
}
