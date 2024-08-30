#!/usr/bin/env node

//=============================================================================================
// IMPORTS
//=============================================================================================
import {exec, spawn} from 'child_process'
import {promisify} from 'util'
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
let currentModelData = null
const appState = {
    currentModel: null,
    models: null,
    spotifyToken: null
};
const BACKEND_URL = 'http://localhost:8040'
//=============================================================================================



//=============================================================================================
// MAIN EVENTS
//=============================================================================================
await welcome()
await getSpotifyToken()


await updateModels(true)
await askModelMultiple()
while (true) {
    resetScreenWithData()
    await displayPrimaryActions()
}
//=============================================================================================




//=============================================================================================
// WELCOME THE USER
//=============================================================================================
async function welcome() {
    //console.clear()
    console.log(chalk.blue('Welcome to playnext. Playnext is a CLI tool that allows you to train neural networks based on low-level audio data.\n'));
    await sleep();
}
//=============================================================================================



//=============================================================================================
// GET THE SPOTIFY TOKEN
//=============================================================================================
async function getSpotifyToken() {
    const execPromise = promisify(exec)

    try {
        const { stdout, stderr } = await execPromise("spotify-token");

        if (stderr) {
            console.error(`stderr: ${stderr}`);
            process.exit(1);
        }

        console.log(stdout)
    } catch (error) {
        console.error(`Error executing spotify-token: ${error.message}`);
        process.exit(1);
    }
}

// async function getSpotifyToken() {
//     const st = spawn("spotify-token")

//     st.stdout.on("data", data => {
//         console.log(`stdout: ${data}`);
//     });

// }



//=============================================================================================


//=============================================================================================
// INITIALIZE MODELS
//=============================================================================================
async function updateModels(initializing) {
    if (initializing) console.log(chalk.green('Before we start, we need to check the models that have already been initialized.'));
    const response = await handleApiCall(
        () => axios.get(`${BACKEND_URL}/models`),
        'Models set succesfully',
        'Error fetching models:'
    )
    appState.models = response.data.models;
    if (initializing) await sleep(500)
    //console.clear()
}
//=============================================================================================



//=============================================================================================
// DISPLAYING DATA
//=============================================================================================
async function resetScreenWithData() {
    //console.clear()
    console.log(`Current Model: ${currentModelData.name}\nNumber of songs trained on: ${currentModelData ? currentModelData.numSongs : 0}\n`);
}
//=============================================================================================



//=============================================================================================
// UPDATING DATA
//=============================================================================================
async function updateCurrentModelData() {
    currentModelData = appState.models.find(model => model.name === appState.currentModel);
}
//=============================================================================================




//=============================================================================================
// ASK WHAT MODEL THE USER WANTS TO CHOOSE, PROVIDING AN INPUT OPTION IF DESIRED
//=============================================================================================
async function askModelMultiple() {
    let choices = appState.models.map(model => ({
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

    appState.currentModel = (answer.model_choice === 'new') ? await getModelInput() : answer.model_choice;
    await updateCurrentModelData()

}

async function getModelInput() {
    const answer = await inquirer.prompt({
        name: 'model_choice',
        type: 'input',
        message: 'New Model:'
    });
    const model_choice = answer.model_choice;
    await initModel(model_choice)
    return model_choice
}

//[ASSOCIATED API CALL]========================================================================
async function initModel(model_name) {
    console.log(chalk.green('Adding model to the database...'));
    const response = await handleApiCall(
        (model_name) => axios.post(`${BACKEND_URL}/models`, { model_name: model_name }),
        'Model added successfully',
        'Error adding model:',
        model_name
    );
    return response.data.name;
}
//=============================================================================================



//=============================================================================================
// DISPLAY THE PRIMARY APP OPTIONS
//=============================================================================================
async function displayPrimaryActions() {
    let choices = ['train the model'];
    if (currentModelData.numSongs > 0) {
        choices.push('train through individual recommendations')
        choices.push('get bulk recommendations')
    }
    choices.push('choose a new model');
    choices.push('end the program');
    const answer = await inquirer.prompt({
        name: 'action_choice',
        type: 'list',
        message: 'What would you like to do with this model?',
        choices: choices
    });
    await resetScreenWithData()
    const action_choice = answer.action_choice;
    switch (action_choice) { // maybe convert this to indices
        case 'train the model':await handleTrainModel();
            break;
        case 'train through individual recommendations':await handleGetSingleRec()
            break;
        case 'get bulk recommendations': await handleGetBulkRecs()
            break;
        case 'choose a new model': await askModelMultiple()
            break;
        case 'end the program':
            //console.clear()
            console.log(chalk.green('Program succesfully aborted'))
            process.exit(1);
            break;
    }
}
//=============================================================================================



//=============================================================================================
// TRAIN THE MODEL WITH BULK TEXT INPUT
//=============================================================================================
async function handleTrainModel() {
    const positiveExamplesInput = await getTrainingInput(true);
    const negativeExamplesInput = await getTrainingInput(false);
    await sendTrainingExamples(positiveExamplesInput, negativeExamplesInput)
}

async function getTrainingInput(isPositive) { // alternate way of readubg input in lines: use promises
    return new Promise((resolve) => {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        console.log(`Input 80-120 Spotify URIs of songs you${isPositive ? '' : ' don\'t'} like. When finished, type "END" on a new line and press Enter:`);

        let uris = [];

        rl.on('line', (line) => {
            if (line === 'END') { rl.close();}
            else if (line.trim() !== '') {uris.push(line.trim());}
        });

        rl.on('close', () => resolve(uris));
    });
}

//=============================================================================================



//=============================================================================================
// FETCH A SINGLE RECOMMENDATION AND GET FEEDBACK
//=============================================================================================
async function handleGetSingleRec() {
    const recommendation_uri = await getRecs(1)
    await handleSingleRecFeedBack(recommendation_uri)
    const answer = await inquirer.prompt({
        name: 'rec_feedback',
        type: 'list',
        message: 'Would you like to continue getting recommendations?',
        choices: ['Yes', 'No']
    });
    if (answer.rec_feedback = 'Yes') await handleGetSingleRec();
}

async function handleSingleRecFeedBack(recommendation_uri) {
    const answer = await inquirer.prompt({
        name: 'rec_feedback',
        type: 'list',
        message: `Here is your recommended song: ${recommendation_uri}
        Did you like this song?`,
        choices: ['Yes', 'No']
    });
    const rec_feedback_positive = answer.rec_feedback == 'Yes';
    console.log('Got it - tuning your recommendations based on that...')
    const negativeExamples = rec_feedback_positive ? [] : [recommendation_uri]
    const positiveExamples = rec_feedback_positive ? [recommendation_uri] : []
    sendTrainingExamples(positiveExamples, negativeExamples)
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
    console.log(`Bulk request successful. Here are your predictions:\n${bulk_recs.map(rec => `${rec}`).join('\n')}`);
    await pressAnyKeyToContinue()
}
//=============================================================================================



//=============================================================================================
// RECOMMENDATION API CALL - USED TO GET SINGLE AND BULK RECOMMENDATIONS
//=============================================================================================
async function getRecs(num_recommendations) {
    console.log('Fetching recommendations')
    const response = await handleApiCall(
        (model_name, num_recommendations) => axios.post(`${BACKEND_URL}/recommendations`, {
            model_name: model_name,
            num_recommendations: num_recommendations
        }),
        currentModelData.name,
        num_recommendations
    );
    return response.data.predicted_uris;
}
//=============================================================================================



//=============================================================================================
// TRAINING API CALL - USED TO TRAIN BULK AND SINGLE RECOMMENDATIONS
//=============================================================================================
async function sendTrainingExamples(positive_examples, negative_examples) {
    console.log('great! training the model now...')

    const response = await handleApiCall(
        (positive_examples, negative_examples) => axios.post(`${BACKEND_URL}/train`, {
            model_name: currentModelData.name,
            positive_examples: positiveExamples,
            negative_examples: negativeExamples,
        }),
        'Model trained succesfully',
        'Error sending examples model:',
        positive_examples,
        negative_examples
    )
    await updateModels(false);
    await updateCurrentModelData()
}
//=============================================================================================
