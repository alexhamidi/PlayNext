#!/usr/bin/env node


//=============================================================================================
import inquirer from 'inquirer'
import axios from 'axios'
import chalk from 'chalk'
import readline from 'readline'
//=============================================================================================



//=============================================================================================
const sleep = (ms = 2000) => new Promise((r) => setTimeout(r, ms));
let currentModelData = null
const appState = {
    currentModel: null,
    models: null
};
const BACKEND_URL = 'http://localhost:8040'
//=============================================================================================



//=============================================================================================
console.clear()
await welcome()
console.clear()
await initializeModels(true)
console.clear()
await askModelMultiple()
//event loop?
while (true) {
    resetScreenWithData()
    await displayPrimaryActions()
    sleep()
    await pressAnyKeyToContinue()
}


//=============================================================================================



//=============================================================================================

async function resetScreenWithData() {
    console.clear()
    await displayCurrentData()
}

async function updateCurrentModelData() {
    currentModelData = appState.models.find(model => model.name === appState.currentModel);
}

async function displayCurrentData() {
    console.log(
`Current Model: ${currentModelData.name}
Number of songs trained on: ${currentModelData ? currentModelData.numSongs : 0}`
    )
}


async function initializeModels(init) { //also update
    if (init) console.log(chalk.green('Before we start, we need to check the models that have already been initialized.'));
    try {
        const response = await axios.get(`${BACKEND_URL}/models`);
        appState.models = response.data.models;
        console.log(chalk.green('Models set succesfully'));
    } catch (error) {
        console.error(chalk.red('Error fetching models:', error));
        process.exit(1)
    }
}

async function welcome() {
    console.log(chalk.blue('Welcome to playnext. Playnext is a CLI tool that allows you to train neural networks based on low-level audio data.\n'));
    await sleep();
}

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

    if (answer.model_choice !== 'new') {
        appState.currentModel = answer.model_choice;
        await updateCurrentModelData()
    } else {
        await askModelInput()
    }
}

async function askModelInput() {
    const answer = await inquirer.prompt({
        name: 'model_choice',
        type: 'input',
        message: 'New Model:'
    });
    const modelChoice = answer.model_choice;
    await initModel(modelChoice)
    appState.currentModel = modelChoice;
    await updateCurrentModelData()
}


async function displayPrimaryActions() {
    let choices = ['train the model'];
    if (currentModelData.numSongs > 0) {
        choices.push('train through individual recommendations')
        choices.push('get bulk recommendations')
    }
    choices.push('end the program');
    const answer = await inquirer.prompt({
        name: 'action_choice',
        type: 'list',
        message: '',
        choices: choices
    });
    await resetScreenWithData()
    const action_choice = answer.action_choice;
    switch (action_choice) {
        case 'train the model':await handleTrainModel();
            break;
        case 'train through individual recommendations':await handleGetSingleRec()
            break;
        case 'get bulk recommendations': await handleGetBulkRecs()
            break;
        case 'end the program':
            console.clear();
            process.exit(1);
            break;
    }
}

async function handleGetBulkRecs() {
    const answer = await inquirer.prompt({
        name: 'num_recommendations',
        type: 'input',
        message: 'How many recommendations would you like?',
    });
    const num_recommendations = answer.num_recommendations;
    const bulk_recs = await getBulkRecs(num_recommendations);
    console.log(`Bulk request successful. Here are your predictions:\n${bulk_recs.map(rec => `${rec}`).join('\n')}`);
}


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
            if (line === 'END') {
                rl.close();
            } else if (line.trim() !== '') {
                uris.push(line.trim());
            }
        });

        rl.on('close', () => {
            resolve(uris);
        });
    });
}


async function handleGetSingleRec() {
    const recommendation_uri = await getSingleRec()
    await handleSingleRecFeedBack(recommendation_uri)
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
    console.log('recommendations tuned succesfully!')
}

async function getBulkRecs(num_recommendations) {
    try {
        console.log('getting recommendation')
        const response = await axios.post(`${BACKEND_URL}/recommendations`, {
            model_name: currentModelData.name,
            num_recommendations: num_recommendations
        })
        const predicted_uris = response.data.predicted_uris
        return predicted_uris
    } catch (error) {
        console.error(chalk.red('Error retreiving recommendation', error.message));
        process.exit(1)
    }
}

async function getSingleRec() {
    try {
        console.log('getting recommendation')
        const response = await axios.post(`${BACKEND_URL}/recommendation`, {
            model_name: currentModelData.name,
        })
        const predicted_uri = response.data.predicted_uri
        console.log(predicted_uri)
        return predicted_uri
    } catch (error) {
        console.error(chalk.red('Error retreiving recommendation', error.message));
        process.exit(1)
    }
}


async function sendTrainingExamples(positiveExamples, negativeExamples) {
    try {
        console.log('great! training the model now...')
        const response = await axios.post(`${BACKEND_URL}/train`, {
            model_name: currentModelData.name,
            positive_examples: positiveExamples,
            negative_examples: negativeExamples,
        })
        await initializeModels(false);
        await updateCurrentModelData()
        console.log(chalk.green('Model trained succesfully'));
    } catch (error) {
        console.error(chalk.red('Error sending examples model:', error.message));
        process.exit(1)
    }
}


async function initModel(modelName) {
    try {
        console.log(chalk.green('Adding model to the database...'));
        const response = await axios.post(`${BACKEND_URL}/models`, {
            model_name: modelName
        });
        await initializeModels(false);
        await updateCurrentModelData()
        console.log(chalk.green('Model added succesfully'));
    } catch (error) {
        console.error(chalk.red('Error adding model:', error.message));
        process.exit(1)
    }
}






async function pressAnyKeyToContinue() {
    await inquirer.prompt([
      {
        type: 'input',
        name: 'continue',
        message: 'Press any key to continue...',
        validate: () => true, // Automatically accept any input
      }
    ]);
  }
