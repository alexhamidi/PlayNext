#!/usr/bin/env node


//=============================================================================================
// IMPORTS
//=============================================================================================
import clipboardy from 'clipboardy'
import inquirer from 'inquirer'
import axios from 'axios'
import chalk from 'chalk'
import readline from 'readline'
import {pressAnyKeyToContinue, handleApiCall} from './utils.js'
//=============================================================================================



//=============================================================================================
// VARIABLES USED THROUGHOUT THE FUNCTION
//=============================================================================================
const sleep = (ms = 2000) => new Promise((r) => setTimeout(r, ms));
const app_state = {
    currentModelName: null,
    currentModelNumSongs: null,
    models: null,
};
const BACKEND_URL = 'http://localhost:8040'
const error = chalk.bold.red;
const success = chalk.green;
const intro = chalk.bold.blue;
//=============================================================================================




//=============================================================================================
// MAIN EVENTS
//=============================================================================================
async function main() {
    await welcome()
    await updateModels(true)
    await askModelMultiple()

    while (true) {
        await resetScreenWithData()
        const action = await displayPrimaryActions()
        await handleAction(action) // happens regardless of this
        if (action === 'end') {
            break;
        } else if (action === 'deletemodel') {
            await askModelMultiple()
        }
    }
}

(async () => {
    try {
        await main();
    } catch (error) {
        console.error(error)
    }
})();

//=============================================================================================




//=============================================================================================
// WELCOME THE USER
//=============================================================================================
async function welcome() {
    console.clear();
    console.log(intro('Welcome to playnext. Playnext is a CLI tool that allows you to train neural networks based on low-level audio data.\n'));
    await sleep();
}
//=============================================================================================




//=============================================================================================
// INITIALIZE MODELS
//=============================================================================================
async function updateModels(initializing=false) {
    if (initializing) console.log('Before we start, we need to check the models that have already been initialized.');
    const response = await handleApiCall(
        () => axios.get(`${BACKEND_URL}/models`),
        'Models set succesfully',
        'Error fetching models:'
    )
    app_state.models = response.data.models;
    await sleep(500)
}
//=============================================================================================




//=============================================================================================
// DISPLAYING DATA
//=============================================================================================
async function resetScreenWithData() {
    console.clear();
    console.log(`Current Model: ${app_state.currentModelName}\nNumber of songs trained on: ${app_state.currentModelNumSongs || 0}\n`);
}
//=============================================================================================




//=============================================================================================
// UPDATE THE STATE OF NUMSONGS
//=============================================================================================
async function updateNumSongs() {
    app_state.currentModelNumSongs = app_state.models.find(model => model.name === app_state.currentModelName)?.numSongs || 0;
}
//=============================================================================================




//=============================================================================================
// ASK WHAT MODEL THE USER WANTS TO CHOOSE, PROVIDING AN INPUT OPTION IF DESIRED
//=============================================================================================
async function askModelMultiple() {
    console.clear()
    let choices = app_state.models.map(model => ({
        name: `${model.name} (${model.numSongs} songs trained)`,
        value: model.name
    }));
    choices.push({ name: 'Input new model', value: 'new' });
    const answer = await inquirer.prompt({
        name: 'model_choice',
        type: 'list',
        message: 'Choose an existing model (if any) or input a new one.',
        choices: choices
    });

    let new_model_name = (answer.model_choice === 'new') ? await getModelInput() : answer.model_choice;
    app_state.currentModelName = new_model_name;
    await updateNumSongs();
}

async function getModelInput() {
    const answer = await inquirer.prompt({
        name: 'model_choice',
        type: 'input',
        message: 'New Model:'
    });
    const model_choice = answer.model_choice;

    const response = await initModel(model_choice);
    await updateModels();
    return model_choice;
}

//[ASSOCIATED API CALL]========================================================================
async function initModel(model_name) {
    console.log(success('Adding model to the database...'));
    const response = await handleApiCall(
        (model_name) => axios.post(`${BACKEND_URL}/models`, { model_name: model_name }),
        'Model added successfully',
        'Error adding model:',
        model_name
    );

    if (response.status === 409) {
        const error = new Error('Error: Model already exists with this name. Try another.');
        error.status = 409;
        throw error;
    }

    return response.data.name;
}
//=============================================================================================




//=============================================================================================
// DISPLAY THE PRIMARY APP OPTIONS
//=============================================================================================
async function displayPrimaryActions() {
    let choices = [
        {name:'train through bulk recommendations', value:'bulktrain'}
    ];

    if (app_state.currentModelNumSongs > 0) choices.push(...[
        {name:'train through individual recommendations', value:'singlerec'},
        {name:'get bulk recommendations', value: 'bulkrec'}
    ]);

    choices.push(...[
        {name:'choose a different model',value:'diffmodel'},
        {name:'delete this model',value:'deletemodel'},
        {name:'end the program',value:'end'}
    ]);

    const answer = await inquirer.prompt({
        name: 'action_choice',
        type: 'list',
        message: 'What would you like to do with this model?',
        choices: choices
    });
    return answer.action_choice;
}

async function handleAction(action) {
    switch (action) {
        case 'bulktrain':
            await handleTrainModel();
            break;
        case 'singlerec':
            await handleGetSingleRec();
            break;
        case 'bulkrec':
            await handleGetBulkRecs();
            break;
        case 'diffmodel':
            await askModelMultiple();
            break;
        case 'deletemodel':
            await handleDeleteModel();
            break;
        case 'end':
            console.log(success('Program successfully aborted'));
            break;
    }
}
//=============================================================================================




//=============================================================================================
// HANDLE MODEL DELETION
//=============================================================================================
async function handleDeleteModel() {
    await deleteModel(app_state.currentModelName);
    app_state.currentModelName = null;
    app_state.currentModelNumSongs = null;
    await updateModels();
}

//=============================================================================================
// TRAIN THE MODEL WITH BULK TEXT INPUT
//=============================================================================================
async function handleTrainModel() {
    const positive_examples_input = await getTrainingInput(true)
    const negative_examples_input = await getTrainingInput(false)

    await sendTrainingExamples(positive_examples_input, negative_examples_input);
    await updateModels();
    app_state.currentModelNumSongs = app_state.models.find(model => model.name === app_state.currentModelName)?.numSongs || 0;
}

async function getTrainingInput(isPositive) { // alternate way of readubg input in lines: use promises
    return new Promise((resolve) => {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        console.log(`Input as many spotify URIs of songs you${isPositive ? '' : ' don\'t'} like as possible. When finished, type 'END' on a new line and press Enter:`);

        let uris = [];

        rl.on('line', (line) => {
            if (line === 'END') { rl.close();}
            else if (line.trim() !== '') {uris.push(line.trim());}
        });

        rl.on('close', () => resolve(uris));

        setTimeout(() => {
            console.log('Input time exceeded. Closing input.');
            rl.close();
        }, 5 * 60 * 1000);
    });
}

//=============================================================================================



//=============================================================================================
// FETCH A SINGLE RECOMMENDATION AND GET FEEDBACK
//=============================================================================================
async function handleGetSingleRec() {
    const recommendation_uri_arr = await getRecs(1);
    const recommendation_uri = recommendation_uri_arr[0];
    clipboardy.writeSync(recommendation_uri)
    await handleSingleRecFeedBack(recommendation_uri);
    const answer = await inquirer.prompt({
        name: 'rec_feedback',
        type: 'list',
        message: 'Would you like to continue getting recommendations?',
        choices: ['Yes', 'No']
    });
    if (answer.rec_feedback === 'Yes') await handleGetSingleRec();
}

async function handleSingleRecFeedBack(recommendation_uri) {
    const answer = await inquirer.prompt({
        name: 'rec_feedback',
        type: 'list',
        message: `Here is your recommended song: ${recommendation_uri}. it has been copied to your clipboard. \nDid you like this song?`,
        choices: ['Yes', 'No']
    });
    const rec_feedback_positive = answer.rec_feedback == 'Yes';
    console.log('Got it - tuning your recommendations based on that...');
    const positive_examples = rec_feedback_positive ? [recommendation_uri] : [];
    const negative_examples = rec_feedback_positive ? [] : [recommendation_uri];
    await sendTrainingExamples(positive_examples, negative_examples)
    await updateModels();
    await updateNumSongs();
}
//=============================================================================================



//=============================================================================================
// FETCH MULTIPLE RECOMMENDATIONS
//=============================================================================================
async function handleGetBulkRecs() {
    const answer = await inquirer.prompt({
        name: 'num_recommendations',
        type: 'input',
        message: 'How many recommendations would you like?',
    });
    const num_recommendations = answer.num_recommendations;
    const bulk_recs = await getRecs(num_recommendations);

    console.log(success('Bulk request succesful.'));

    const rec_string = bulk_recs.join('\n');

    console.log(`Here are your predictions:\n${rec_string}\n`);
    clipboardy.writeSync(rec_string);
    console.log(success('Songs succesfully copied to clipboard'))

    await pressAnyKeyToContinue();
}
//=============================================================================================



//=============================================================================================
// RECOMMENDATION API CALL - USED TO GET SINGLE AND BULK RECOMMENDATIONS
//=============================================================================================
async function getRecs(num_recommendations) {
    console.log(`Fetching recommendation${num_recommendations===1?'':'s'}`);
    const response = await handleApiCall(
        (model_name, num_recommendations) => axios.post(`${BACKEND_URL}/recommendations`, {
            model_name: model_name,
            num_recommendations: num_recommendations
        }),
        `recommendation${num_recommendations===1?'':'s'} sent successfully`,
        'Error sending recommendations:',
        app_state.currentModelName,
        num_recommendations
    );
    return response.data.predicted_uris;
}
//=============================================================================================



//=============================================================================================
// TRAINING API CALL - USED TO TRAIN BULK AND SINGLE RECOMMENDATIONS
//=============================================================================================
async function sendTrainingExamples(positive_examples, negative_examples) {
    console.log('Great! Training the model now...');

    const response = await handleApiCall(
        (positive_examples, negative_examples) => axios.post(`${BACKEND_URL}/train`, {
            model_name: app_state.currentModelName,
            positive_examples: positive_examples,
            negative_examples: negative_examples,
        }),
        'Model trained successfully',
        'Error sending examples to model:',
        positive_examples,
        negative_examples
    );
}
//=============================================================================================



//=============================================================================================
// API CALL TO DELETE A MODEL
//=============================================================================================
async function deleteModel(model_name) {
    console.log('Deleting the model...');

    const response = await handleApiCall(
        () => axios.delete(`${BACKEND_URL}/models/${model_name}`),
        'Model deleted successfully',
        'Error deleting model:'
    );
}
//=============================================================================================




