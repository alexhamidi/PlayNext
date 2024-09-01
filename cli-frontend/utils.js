import chalk from 'chalk'
import inquirer from 'inquirer'

export async function pressAnyKeyToContinue() {
    await inquirer.prompt([
      {
        type: 'input',
        name: 'continue',
        message: 'Press any key to continue...',
        validate: () => true, // Automatically accept any input
      }
    ]);
}

export async function handleApiCall(apiFunction, successMessage, failureMessage, ...args) {
  try {
      const response = await apiFunction(...args);
      console.log(chalk.green(successMessage));
      return response;
  } catch (error) {
      if (error.response && error.response.status === 409) {
          return error.response;
      } else {
          console.error(chalk.red(failureMessage, error.message));
          process.exit(1)
      }
  }
}


