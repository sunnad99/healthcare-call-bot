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
