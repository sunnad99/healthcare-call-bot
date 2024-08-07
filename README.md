# Healthcare Call Bot

# Remaining documentation things:

- [ ] Add a section on how to deploy to render.com

- [ ] Add a section about how the CRM data was retrieved

- [ ] move prompt related information to another .md file and add a hyperlink in readme.md to that file
      (prompts.md)

- [ ] Move detailed route information of how exactly routes work from readme.md and put in another file
      (routes.md)

- [ ] make a flow diagram of how the information will flow

- [ ] Add pictures of the used technologies

- [ ] talk about how each problem was solved and tackled
  - skip logic for questions
  - Creation of dynamic questionnaires for each individual

# Technologies Used (TODO)

![](https://github.com/sunnad99/crm-callbot-api/blob/db136fa8335ecbc264eee469aeb490a85b5e98e7/img/bland.ai%20image.jpg)
_Bland.Ai_

![](https://github.com/sunnad99/crm-callbot-api/blob/4a856cbbb5889cbd68d17a515ddbcdc51e46e4f3/img/fastapi%20image.png)
_FastAPI_

![](https://github.com/sunnad99/crm-callbot-api/blob/4a856cbbb5889cbd68d17a515ddbcdc51e46e4f3/img/pandas%20image.png)
_Pandas_

![](https://github.com/sunnad99/crm-callbot-api/blob/4a856cbbb5889cbd68d17a515ddbcdc51e46e4f3/img/render.com%20image.png)
_Render_

This is a CRM call bot that is used to automate the process of calling patients and asking them questions about their visit to the hospital. The bot asks questions from a questionnaire, records the answers, and then sends the data to the hospital's CRM system.

# Flow diagram (TODO)

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

   - EMAIL -> Provided by hospital CRM
   - PASSWORD -> Provided by hospital CRM
   - USER_KEY -> Base64 encoded string of your IPV4 address (could be set as a blank string too)
   - BLAND_API_KEY -> API key from the bland.ai website

6. Run the application by running
   `python app.py`

**NOTE:** The API will be able to run and create the pathways but the webhook calls will not work as the webhook URL will be localhost. To test the webhook calls, you will need to deploy the application to a server. For this, you can use Render.com (or any other hosting service).

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

## Pathway creation route

Before iteration of each question, all the dynamic data from visit infos should be set

Iterate over each question and create a "default" node: - For questions with answers, create a webhook node as well
NOTE: when moving from a question with an answer to a question with no answer, it should just go directly to the normal node

    A normal node needs the following params:
    name — name of the node
    isStart — whether the node is the start node. There can only be 1 start node in a pathway. Either true or false.
    type — Type of the node. Can be Default, End Call, Transfer Node, Knowledge Base, or Webhook.
    text — If static text is chosen, this is the text that will be said to the user.
    prompt — If dynamic text is chosen, this is the prompt that will be shown to the user.
    extractVars
    An array of array of strings. [[varName, varType, varDescription]] e.g [["name", "string", "The name of the user"], ["age", "integer", "The age of the user"]]

    A webhook node might need all of the above and also:
    url — The URL of the webhook
    body: The body of the webhook that will consist of the data that will be sent to the webhook
    method: The method of the webhook. Can be GET, POST, PUT, DELETE
    responseData: array of objects from which the data from the API will be extracted from
        NOTE: Each object here has 3 fields
        - data
        - name
        - context
    responsePathways: The pathways that will be followed based on the response from the webhook
        NOTE: Each element is an array itself, which has 4 different elements
            - name of the variable in the pathway
            - the condition e.g. "=="
            - the value that it should be matched to
            - the object that will be used for routing to the correct node
                - id
                - name
    extractVars: Array of arrays for extracting data before making a call to the webhook
        - name of variable
        - dtype of var
        - prompt for variable for extracting

## Skip Logic Detection route

Inputs:

- logic (array of objects): consists of all the questions that need to be skipped
- history (array of objects): contains all the answered (and unanswered questions)

Using the history, determine if the next question in line needs to be answered or not.
NOTE: the history will have some questions that have no answers and are set up with curly braces - set their values to NULL before moving on to determining if the next question needs to be asked or not

The next question is determined by taking the id of the last element in the history and adding 1 to it
NOTE: Only the last question will not have a webhook to go to

in the response, we just return a boolean:

- True if the pathway should continue to the next question
- False if the pathway should skip the question

NOTE: If the question is to be skipped, the next pathway should be the webhook node of the next question:
e.g. if we are on question 2's webhook response and question 3 is being skipped
then we should go to the webhook node AFTER question 3 (which will be question 4's webhook node)

NOTE#2: For every webhook node, the history will consist of ALL the past answers.

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
