

//make an error page
$(document).ready(async () => {
    try {
        await setupNavigation();
        await loadPage(location.pathname); // Load the current page on initial load
    } catch (error) {
        console.error('Error during initial setup:', error);
        alert('An error occurred during initialization. Please try again later.');
    }
});

async function setupNavigation() {
    $('nav a').on('click', async function(e) {
        e.preventDefault();
        const page = $(this).attr('href');
        try {
            await loadPage(page);
        } catch (error) {
            console.error('Error loading page on navigation:', error);
        }
    });

    $(window).on('popstate', async function() {
        try {
            await loadPage(location.pathname);
        } catch (error) {
            console.error('Error loading page on popstate:', error);
        }
    });
}

async function handleLoadStart() {
    try {
        await populateModels();
        setupExistingModelForm();
        setupNewModelForm();
    } catch (error) {
        //if error is a server error
        console.error('Error handling load start:', error);
        await loadPage('servererror.html');
    }
}

async function handleLoadIndex() {
    try {
        handleNoModelRedirect();
        setupHeader();
    } catch (error) {
        //if error is a server error\
        console.error('Error handling load index:', error);
        await loadPage('servererror.html');
    }
}

async function handleLoadTrain() {
    try {
        handleNoModelRedirect();
        setupHeader();
        await setupTrainingForm();
    } catch (error) {
        //if error is a server error
        console.error('Error handling load train:', error);
        await loadPage('servererror.html');
    }
}

async function handleLoadRecs() {
    try {
        handleNoModelRedirect();
        setupHeader();
        startRecs();
    } catch (error) {
        //if error is a server error
        console.error('Error handling load recs:', error);
        await loadPage('servererror.html');
    }
}

async function setupHeader() {
    try {
        const current_model = localStorage.getItem('current_model');
        const models = JSON.parse(localStorage.getItem('models'));
        const model_num_songs = models[current_model];
        $('#model-name').text(current_model);
        $('#model-num-songs').text(model_num_songs);
    } catch (error) {
        console.error('Error setting up header:', error);
    }
}

function handleNoModelRedirect() {
    const current_model = localStorage.getItem('current_model');
    if (current_model === null) {
        console.error('Error - no model selected');
        loadPage('start.html');
        return;
    }
    const models = JSON.parse(localStorage.getItem('models'));
    if (models === null || !(current_model in models)) {
        console.error(`Error - training data not available for ${current_model}`);
        loadPage('start.html');
    }
}

async function populateModels() {
    const models = await get_all_models();
    localStorage.setItem('models', JSON.stringify(models));
}

function setupNewModelForm() {
    const models = localStorage.getItem('models');
    const modelsObj = JSON.parse(models);
    if (models === null) {
        console.error('Models not properly loaded');
        return;
    }
    if (Object.keys(modelsObj).length === 0) {
        $('<p>').text('No models exist here (yet)').appendTo('#existing-area');
    } else {
        $('<form>')
            .append(
                $('<select>')
                .attr('id', 'model-select')
                .attr('name', 'model-select')
                .append($('<option>').text('Select a model').attr('value', ""))
            )
            .appendTo('#existing-area');
        $.each(modelsObj, function(model_name, num_songs_trained) {
            $('<option>')
                .attr('value', model_name)
                .text(`${model_name} (${num_songs_trained}) songs trained on`)
                .appendTo('#model-select');
        });
    }
}

function setupExistingModelForm() {
    $("#new-model-form").on("submit", async function(e) {
        e.preventDefault();
        const model_name = $("#new-model-input").val();
        const models = JSON.parse(localStorage.getItem('models')) || {};
        if (model_name === '') {
            console.log('Need to input');
            return;
        }
        const model_exists = model_name in models;
        if (model_exists) {
            console.log('Model already exists with that name');
        } else {
            await init_model(model_name);
            localStorage.setItem("current_model", model_name);
            // Navigate to the homepage or update UI accordingly
        }
    });
}

async function setupTrainingForm() {
    $("#training-form").on("submit", async function(e) {
        e.preventDefault();
        const positive_examples = $("#positive-examples").val();
        const negative_examples = $("#negative-examples").val();
        try {
            await send_training_examples(positive_examples, negative_examples);
            await populateModels();
        } catch (error) {
            console.error('Error sending training examples:', error);
            alert('An error occurred while sending training examples. Please try again.');
        }
    });

    $("#end-model-session").on("click", function(e) {
        localStorage.clear();
        location.reload();
    });
}

async function startRecs() {
    //TODO
}

async function loadPage(url) { // Handle page loading
    console.log(url);
    try {
        const data = await $.ajax({
            url: url,
            method: 'GET',
            contentType: 'text/html'
        });
        const bodyContent = $(data).find('body').html();
        $('body').html(bodyContent);
        window.history.pushState({path: url}, '', url);
        const currentPage = $('body').data('page');
        console.log(currentPage);
        if (currentPage === 'server-error') return
        switch(currentPage) {
            case 'start':
                await handleLoadStart();
                break;
            case 'index':
                handleLoadIndex();
                break;
            case 'train':
                await handleLoadTrain();
                break;
            case 'recs':
                handleLoadRecs();
                break;
            default:
                console.error('Unknown page:', currentPage);
                break;
        }
    } catch (error) {
        console.error('Error loading page:', error);
    }
}

/*******************************
API REQUESTS
*******************************/

function get_all_models() { // Retrieve all models
    return new Promise((resolve, reject) => {
        $.ajax({
            url: 'http://localhost:8040/models',
            method: 'GET',
            contentType: 'application/json',
            success: (response) => {
                console.log(response.message);
                resolve(response.all_models);
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
            url: 'http://localhost:8040/models',
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

function send_training_examples(positive_examples, negative_examples) {
    const model_name = localStorage.getItem("current_model");
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
