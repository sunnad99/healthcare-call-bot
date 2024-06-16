YOUR_NAME = "Jordan"

QUESTION_WITH_ANSWERS_PROMPT = """Ask the question from the user the question, delimited by 3 backticks, which is shown below.
                Don't include the backticks when asking the question. Also, include the possible answers in the question, retrieved
                from the answers of the question, delimited by 3 dollar signs, shown below. Rephrase the answers in a way that its understandable in a
                conversation on a phone call with someone. This also includes the fact that the provided options should be human readable and shouldn't contain any special characters.
                And of course, don't include the dollar signs when asking the question with the possible answers. Also, don't show "not applicable" as an option.

                ```
                {quest_text}
                ```

                $$$
                {quest_answer}
                $$$

                TOP TOP PRIORITY: Don't prematurely end a survey when there are still more questions left unless the user says that they don't want to continue the survey anymore.
                To find out what the current question is, see below the current question number and the total number of questions in the questionnaire delimited by 3 ampersands.

                &&&
                The current question is {question_num} out of {total_questions}.
                &&&

                VERY VERY IMPORTANT: Make sure the question isn't verbose and is straight to the point.

                """

QUESTION_WITHOUT_ANSWERS_PROMPT = """Ask the question from the user the question, delimited by 3 backticks, which is shown below.
                Don't include the backticks when asking the question.

                ```
                {quest_text}
                ```
                """

COMMENTS_QUESTION_EXTRA_PROMPT_INFO = """
If the user doesn't reply with any specific names or titles e.g. he/she, they, them, etc., ask them who they are referring to.
If the user gives a gives a vague answer that doesn't provide any useful information e.g. "It was good", ask them to provide more details or to be more specific.
If the user elaborates properly and provides enough details, respond by letting them know that you took note of it.
If the user says "I don't have any comments", "I don't have anything to say", "I don't have any feedback", "I don't have any suggestions", "I don't have anything to add" or anything along those lines,
respond by thanking them and moving on to the next question.
"""

CLARIFYING_QUESTION_MAX_ATTEMPTS_PROMPT = """
Don't move on to the next node before extracting an acceptable answer that closely matches the answers shown above, delimited by 3 dollar signs, or retrying up to a maximum of 3 tries only when invalid responses are given UNLESS the user wants to move on from the question for example by stating "not applicable", "neither", "none of the above", "I'm not sure", "I don't know", "I don't remember" or anything else along those lines unless the user's response to a Likert scale question is negative or fair, then ask them to elaborate.

ALSO VERY VERY IMPORTANT: After a person provides an accepted answer, don't repeat the answer and move on to the next question unless the question is a Likert scale question and the answer is negative or fair, in which case, ask for justification.
Only once they have provided that justification for their negative or fair response for Likert scale questions, move on to the next question.

VERY VERY IMPORTANT: If the provided answer lies between multiple numerical options for example the options are 0-1, 2-5, 6-10, and 10-20 and the user answered as "3 to 15", ask a clarification question to choose between the relevant options. In this case, the clarification question would
include 3 different options, "2-5", "6-10", "10-20" and the user would choose from one of those provided options. For example, "If you had to choose between 2-5, 6-10, and 10-20, which one would you choose?".

EXTREMELY IMPORTANT: For Likert scale questions, if the user's answer is ambiguous (e.g., they say 'great' when the options are poor, fair, good, or excellent), the bot should ask a clarifying question, such as 'If you had to choose between good and excellent, which one would you choose?' If the user's clarified response is negative or 'fair,' the bot should then ask them to elaborate on why their experience was negative or fair.
But, if the user provided an answer that is neutral and can have multiple meanings for example "it was alright" or "it was ok", then state all the options again and ask them to choose one.
For example if all the options were "poor", "fair", "good", and "excellent" and the user said "it was alright", ask them to choose between all the options again.

EXTREMELY IMPORTANT: For Yes and No questions, if the user provides an answer that is not a clear "Yes" or "No" for example "I guess", "I suppose", "I think so", "Maybe", "I believe not", "I think not", "maybe not", or anything else along those lines, ask them to provide a clear "Yes" or "No" answer.

Remember, this doesn't mean that the call should be ended, but rather that the question should be skipped and the next question should be asked."""


QUESTION_WITH_ANSWER_CONDITION_EXAMPLE = """

TOP MOST PRIORITY:
#############################
For Likert scale questions, if the answer has a negative or fair feeling, always ask for a comment about why the user thinks that way.
If you do not ask the user why they are feeling negative or fair, then the condition will fail.
#############################


TOP PRIORITY:
#############################
Don't move on to the next node before extracting an acceptable answer that closely matches the answers shown below, delimited by 3 dollar signs, or retrying up to a maximum of 3 tries only when invalid responses are given UNLESS the user wants to move on from the question for example by stating "not applicable", "neither", "none of the above" or anything else along those lines, then just move on to the next node unless the user's response to a Likert scale question is negative or fair, then ask them to elaborate.
For Likert scale questions, if the user provided an answer that is neutral and can have multiple meanings for example "it was alright" or "it was okay", then state all the options again and ask them to choose one UNLESS "alright" was said in an unambiguous context.
For Likert scale questions, if the user's answer is ambiguous (e.g., they say 'great' when the options are poor, fair, good, or excellent), the bot should ask a clarifying question, such as 'If you had to choose between good and excellent, which one would you choose?' If the user's clarified response is negative or 'fair,' the bot should then ask them to elaborate on why their experience was negative or fair.
For numerical based questions, this includes questions with range based answers, if the provided answer lies between multiple numerical options for example the options are 0-1, 2-5, 6-10, and 10-20 and the user answered as "3 to 15", ask a clarification question to choose between the relevant options. In this case, the clarification question would
include 3 different options, "2-5", "6-10", "10-20" and the user would choose from one of those provided options. For example, "If you had to choose between 2-5, 6-10, and 10-20, which one would you choose?".
For Yes and No questions, if the user provides an answer that is not a clear "Yes" or "No" for example "I guess", "I suppose", "I think so", "Maybe", "I believe not", "I think not", "maybe not", or anything else along those lines, ask them to provide a clear "Yes" or "No" answer.

#############################



SECOND PRIORITY:
#########################
VERY VERY IMPORTANT: If the user's response is "not applicable", "neither", "none of the above", "I'm not sure", "I don't know", "I don't remember" or anything else along those lines, treat it as "not applicable", don't repeat the response and then just move on to the next node.
VERY VERY IMPORTANT: No need to provide reaffirmation when the user's answer has matched the answer from the given options, just move straight to the next question unless the question is a Likert scale question and the answer is negative or fair, in which case, ask for justification.
Only once they have provided that justification for their negative or fair response for Likert scale questions, respond by letting them know that you took note of it and then move on to the next question.
##########################


THIRD PRIORITY:
##########################
VERY VERY IMPORTANT: Don't ask any other question that is not relevant to the main question, delimited by 3 backticks shown below.
##########################

```
{quest_text}
```

$$$
{quest_answer}
$$$

"""


ANSWER_ID_TEMPLATE = {
    "name": "answerID{question_num}",
    "type": "integer",
    "value": r"""
            The answers, with their ids,
            delimited by 3 backticks,
            are stored in an array of objects below.
            Match the answer of the user to one of the answers below as accurately as possible.
            Extract the answer Id of the question.

            Don't set it as an object as it causes an exception and breaks the entire bot.
            e.g. of a bad answer -> {"value":2}
            e.g of a bad answer -> {}
            e.g. of a good answer -> 2
            e.g. of a good answer -> null

            Also, make sure to set the answer as an integer.
            Make sure that when the reply from user is ambiguous, set the id associated with "N/A" as the id for the given question
            For example, if the answer object is {"id": 5, "title": "N/A"}, set the answer as 5.

            ```
            {answers}
            ```
        """,
}

ANSWER_TEXT_TEMPLATE = {
    "name": "answerText{question_num}",
    "type": "string",
    "value": """
            Whatever the user replies with, based on the context of the question, store that as their answer over here.
            If the user doesn't reply with any specific names or titles e.g. he/she, they, them, etc., ask them who they are referring to.
            If the user gives a gives a vague answer that doesn't provide any useful information e.g. "It was good", ask them to provide more details or to be more specific.
            If the user elaborates properly and provides enough details, respond by letting them know that you took note of it.
            If the user says "I don't have any comments", "I don't have anything to say", "I don't have any feedback", "I don't have any suggestions", "I don't have anything to add" or anything along those lines,
            respond by thanking them and moving on to the next question.
        """,
}
