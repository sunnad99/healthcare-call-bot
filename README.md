# Healthcare Call Bot

# Remaining documentation things:

- [x] Add a section on how to deploy to render.com

- [ ] Add a section about how the CRM data was retrieved

- [ ] move prompt related information to another .md file and add a hyperlink in readme.md to that file
      (prompts.md)

- [x] Move detailed route information of how exactly routes work from readme.md and put in another file
      (routes.md)

- [x] make a flow diagram of how the information will flow

- [x] Add pictures of the used technologies

- [ ] talk about how each problem was solved and tackled
  - skip logic for questions
  - Creation of dynamic questionnaires for each individual

<table>
<tr>

<td align="center">
<a href="https://bland.ai">
  <img src="img/bland.ai image.jpg" alt="Bland.AI">
</a>
  <p><em>Bland.AI</em></p>
</td>

<td align="center">
<a href="https://fastapi.tiangolo.com/">
  <img src="img/fastapi image.png" alt="FastAPI">
</a>
  <p><em>FastAPI</em></p>
</td>

<td align="center">
<a href="https://pandas.pydata.org/">
  <img src="img/pandas image.png" alt="Pandas">
</a>
  <p><em>Pandas</em></p>
</td>

<td align="center">
<a href="https://render.com">
  <img src="img/render.com image.png" alt="Render">
</a>
  <p><em>Render</em></p>
</td>

</tr>
</table>

This is a CRM call bot that is used to automate the process of calling patients and asking them questions about their visit to the hospital. The bot asks questions from a questionnaire, records the answers, and then sends the data to the hospital's CRM system.

# Flow diagram

<div align="center">
  <img src="img/CRM Callbot flowchat.png" alt="Flowchart">
</div>

# Features

- Automated calls to patients

- Secure retrieval of questionnaire data

- Dynamic patient information handling with questionnaire

- Skip logic for questions based on answer history

- Clever decision making, through prompting, to handle questions can be of various types, providing accurate responses

- Calls can be ended prematurely with the data being saved for later submission

# Prerequesites

1. Github.com Account: For version control
2. Render.com Account: For hosting the bot
3. Bland.ai Account: For creating AI pathways

# Local Setup

**Important**: Make sure to have python 3.11.4 installed with the the **Add Python 3.11 to PATH** option checked.

1. Clone the repository
2. Create a virtual environment by running
   `python -m venv venv`
3. Activate the virtual environment by running

   - On Windows: `.\venv\Scripts\activate`
   - On MacOS/Linux: `source venv/bin/activate`

4. Install the dependencies by running
   `pip install -r requirements.txt`

5. Make sure to create a `.env` file and add the following variables:

   - SERVICE_BASE_URL -> Base URL of this current call bot service. For local development, it should be `http://localhost:8000`
   - EMAIL -> Provided by hospital CRM
   - PASSWORD -> Provided by hospital CRM
   - USER_KEY -> Base64 encoded string of your IPV4 address (could be set as a blank string too)
   - BLAND_API_KEY -> API key from the bland.ai website
   - GSPREAD_SECRET_FILE -> Path to the google service account json file
   - GSPREAD_SHEET_ID -> ID of the google sheet where the data is to be stored

     - NOTE: This can be retrieved from the google sheets link for example in the link below,

       https://docs.google.com/spreadsheets/d/abcxyz/edit?gid=0#gid=0

       the sheet ID is the part after the `/d/` and before the `/edit`
       so the sheet ID in this case would be `abcxyz`

6. Run the application by running the following command
   `uvicorn app:app --host 0.0.0.0`

**NOTE:** The API will be able to run and create the pathways but the webhook calls will not work as the webhook URL will be localhost. To test the webhook calls, you will need to deploy the application to a server. For this, you can use Render.com (or any other hosting service).

# Cloud Deployment (Render.com)

1. Register and login to Render (preferrably with Github)
2. Click on New -> Web Service
3. Choose the repository
4. Then, on the normal settings, follow the below steps:

   - Provide a name
   - Choose your region
   - Set the start command as
     `uvicorn app:app --host 0.0.0.0`
   - Set the environment variables:
     - PYTHON_VERSION to "3.11.4"
   - SERVICE_BASE_URL to the base URL of the service (for example, `https://your-service-name.onrender.com`)
   - EMAIL to your email which is used on the CRM
   - PASSWORD as the password used on the CRM account
   - USER_KEY as a base64 encoded string of your IPV4 address (could be set as a blank string too)
   - BLAND_API_KEY as the API key obtained from bland.ai
   - GSPREAD_SECRET_FILE as the path to the google service account json file (see note at the end of this section)
   - GSPREAD_SHEET_ID as the ID of the google sheet where the data is to be stored

5. In the advanced settings, set the following:

   - Set the Health Check to "/"
   - Choose the auto deploy. If yes, then everytime a commit is pushed, the service will redploy automatically.

6. Once done, click "Deploy Web Service"

**NOTE:** The google service account json file is the file that is downloaded from the google cloud console when you create a service account. This file is used to authenticate the google sheets API. Make sure to upload this file to the service and set the path in the environment variables.

See more information on how to create a service account and download the json file here:
https://docs.gspread.org/en/latest/oauth2.html

# API Routes

## `GET` Survey

This endpoint is used to get the survey's metadata i.e. the project information. This endpoint only returns the data for a single project.

#### Inputs

surveyor_id (int): The ID of the surveyor who is calling the patient

#### Outputs

Entire JSON object that entails all the necessary information about the project

## `GET` Calls

This endpoint is focused on obtaining the patient's information from the CRM system. Every call made to this API endpoint will return the data of a different patient.

#### Inputs

project_id (int): The ID of the project's questionnaire
surveyor_id (int): The ID of the surveyor who is calling the patient

#### Outputs

Entire JSON object that entails all the necessary information about the patient (including data to be used in the survey)

## `GET` Questionnaire

This endpoint is used to get the entire questionnaire for the project. This includes the skip logic, the questions, and the answers.

#### Inputs

project_id (int): The ID of the project's questionnaire
surveyor_id (int): The ID of the surveyor who is calling the patient

#### Outputs

questionnaire (array of objects): Includes each question and its possible answers

logic (array of objects): The skip logic for each question

## `POST` Send Call

The endpoint does the following steps in order:

- Extracts only the necessary fields from the questionnaire and replaces all the placeholder values with the patient's data
  - question id
  - question text
  - answer
- Creates and updates the pathway for the project (using the bland.ai API)

  - Forms all the nodes and edges for every question in the questionnaire

- Sends a call to the patient, utilizing the newly created pathway for the conversation

#### Inputs

quest_data (object): The questionnaire data that is to be sent to the patient. This includes

- questionnaire
- logic

caller_data (object): The data of the patient that is to be called. The format of this object is the same as the output of the `GET` Calls endpoint

#### Outputs

message (str): A message that tells the user that the call has been sent

pathway_id (str): The bland.ai ID of the pathway that was created for the conversation

## `POST` Skip Question

This endpoint is used to determine if the next question in the questionnaire should be asked or not. This is done by checking the history of the patient's answers and the skip logic for the next question.

#### Inputs

skip_logic (array of objects): The skip logic for the question
answer_history (array of objects): The history of the patient's answers
question_id (int): The ID of the question that is to be asked next

#### Outputs

proceed (bool): A boolean that tells the user if the next question should be asked or not

## `POST` Submit Questionnaire

This endpoint is used to submit the answers of the patient to the CRM system given they have answered all the questions. If the patient has not answered all the questions, the data is saved in a temporary storage (excel sheet in our case).

This endpoint is called by the pathway if a call ends prematurely for a plethora of reasons or if the questionnaire is completed.

#### Inputs

variables (object): The webhook data returned from the pathway
The object inludes the following fields:

- pathway_id (str): The ID of the pathway that was used for the conversation
- pathway_name (str): The name of the pathway that was used for the conversation
- questionnaire (array of objects): The questionnaire that was used for the conversation
- chcs_call_id (int): The ID of the call that was made to the patient
- phone_number (str): The phone number of the patient formatted to E.164 standards

#### Outputs

message (str): A message that tells the user that the answers have been submitted

# Future Aspects

This section will include the future aspects of the project that could be implemented to make the project more robust and efficient. It also includes additional functionalities that will be added on top to make the project more functional.

- [ ] Make.com/Zapier automation to call new patients automatically at regular intervals
      NOTE: Right now, the calls are made manually by the surveyor.

- [ ] Use a database to store calls information instead of excel sheets

- [ ] An automation for recalling patients who:

  - Did not answer the call
  - Did not answer all the questions
  - Call dropped for problems on the patient's end
  - Call dropped for problems on the bot's end

- [ ] Fine tune prompts for the questions to be more accurate and precise to what the surveyor wants to ask
