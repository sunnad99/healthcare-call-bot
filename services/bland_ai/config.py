QUESTION_PROMPT = """Ask the question from the user the question, delimited by 3 backticks, which is shown below.
                Don't include the backticks when asking the question.

                ```
                {quest_text}
                ```
                If you are not able to extract information, rephrase the question and ask again in a way that considers the answers,
                delimited by 3 dollar signs, shown below. Rememeber to not include the dollar signs when asking the question.

                $$$
                {quest_answer}
                $$$
"""

ANSWER_TEMPLATE = {
    "name": "answerID{question_num}",
    "type": "integer",
    "value": """
            The answers, with their ids,
            delimited by 3 backticks,
            are stored in an array of objects below.
            Match the answer of the user to one of the answers below as accurately as possible.
            Extract the answer Id of the question.
            ```
            {answers}
            ```
        """,
}
