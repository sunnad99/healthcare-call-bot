import json
import pandas as pd

from .config import (
    CLARIFYING_QUESTION_MAX_ATTEMPTS_PROMPT,
    COMMENTS_QUESTION_EXTRA_PROMPT_INFO,
    QUESTION_WITH_ANSWER_CONDITION_EXAMPLE,
    YOUR_NAME,
)
from .utils import create_question_node, create_webhook_node, fill_placeholders
from config import SERVICE_BASE_URL


def extract_answers(row, patient_lang_id):

    answers = row["answer"]
    answer_ids = row["ansId"]

    if not answer_ids:
        return []

    def format_answers(answer):

        ans_id = answer.get("id")
        if not ans_id:
            return

        answer_text = list(filter(lambda x: x["langId"] == patient_lang_id, answer["langAnswers"]))[0]["ansText"]

        return {"id": ans_id, "ansText": answer_text}

    formatted_answers = list(map(format_answers, answers))

    return formatted_answers


## Bland.ai main functions
def extract_questionnaire_text(quest_data: dict, caller_data: dict, lang_id: int) -> pd.DataFrame:

    quest_df = pd.DataFrame(quest_data["questionnaire"])
    question_df = quest_df["question"].apply(pd.Series).explode("langQuestions")
    question_df[["langId", "quesText"]] = question_df.langQuestions.apply(pd.Series)[["langId", "quesText"]]

    filtered_lang_questions_df = question_df[question_df["langId"] == lang_id].drop(columns=["langQuestions", "langId"])

    filtered_lang_questions_df["quesText"] = filtered_lang_questions_df.apply(
        fill_placeholders, caller_data=caller_data, axis=1
    )

    quest_with_text_df = quest_df.merge(
        filtered_lang_questions_df[["id", "quesText", "title", "category"]], left_on="quesId", right_on="id", how="left"
    ).drop(columns=["question", "id"])

    # Replace the placeholder with the name of the AI caller
    quest_with_text_df.loc[quest_with_text_df.sequence == 1, "quesText"] = quest_with_text_df.loc[
        quest_with_text_df.sequence == 1, "quesText"
    ].str.replace("___", YOUR_NAME)

    return quest_with_text_df


def create_nodes_and_edges(quest_with_text_df: pd.DataFrame, quest_data: dict) -> tuple:

    skip_logic = quest_data["logic"]

    nodes, edges, current_quest = [], [], None
    skip_logic_df = pd.DataFrame(skip_logic).astype({"questionId": "Int64", "answerId": "Int64"})
    total_questions = len(quest_with_text_df)
    for index in range(1, len(quest_with_text_df)):

        prev_quest, current_quest, next_quest = (
            quest_with_text_df.iloc[index - 1],
            quest_with_text_df.iloc[index],
            None,
        )

        prev_quest_id = prev_quest["sequence"]
        prev_quest_title = prev_quest["title"].lower()
        prev_quest_text = prev_quest["quesText"]
        prev_quest_answer = prev_quest["answer"]

        current_quest_id = current_quest["sequence"]
        current_quest_text = current_quest["quesText"]
        current_quest_answer = current_quest["answer"]
        current_quest_affected_data = skip_logic_df[skip_logic_df.affectedQuestionId == current_quest_id]

        next_quest_id, next_quest_affected_data = None, None
        if index < len(quest_with_text_df) - 1:

            next_quest = quest_with_text_df.iloc[index + 1]
            next_quest_id = next_quest["sequence"]
            next_quest_affected_data = skip_logic_df[skip_logic_df.affectedQuestionId == next_quest_id]

        # Handling intro questions at the start of the survey
        # TODO: Skip response from user for question 19
        if "introduction" in prev_quest_title and "provider" not in prev_quest_title:

            extra_prompt_info = """If a user asks "Who is this?" or "Who do you work for?", respond by letting the person know who you are and/or where you are from.

If a user asks "What is this about?" or "Why are you calling?" or "What is the purpose of this survey?", "Is this confidential?",
respond by letting them know what the survey/questionnaire is actually about and that it is confidential.

VERY VERY IMPORTANT: If the user says "Now's not a good time", "I'm busy right now",
"I didn't see them", "I don't remember that visit", "I'm uncomfortable", "I'm not interested", "I still would rather not take a survey", "I am not in the mood"
or any answer that shows overall feeling of rejection to the given question, respond by providing the respective answer based on the context of the question.
For example, if the question is "Were you present with your child during this visit?" and the user says something like "No", the response would be
"Ok, well we were just calling to see how the recent visit went. But since you weren't there or don't remember we won't go through with the survey. You have a phenomenal day!"
The call should end right here immediately after the response is given.
"""

            prev_node = create_question_node(
                prev_quest_id,
                prev_quest_text,
                prev_quest_answer,
                extra_prompt_info=extra_prompt_info,
            )

        elif prev_quest.category.lower() == "comments":

            prev_node = create_question_node(
                prev_quest_id, prev_quest_text, prev_quest_answer, extra_prompt_info=COMMENTS_QUESTION_EXTRA_PROMPT_INFO
            )
            if current_quest.category.lower() == "service recovery":
                print("Service Recovery Question Found...")

                satisfied_quest = quest_with_text_df[quest_with_text_df.title.str.contains("Satisfied Closing")].iloc[0]
                satisfied_quest_id = satisfied_quest["sequence"]
                satisfied_quest_text = satisfied_quest["quesText"]
                satisfied_quest_answer = satisfied_quest["answer"]

                service_recovery_quest_node = create_question_node(
                    current_quest_id,
                    current_quest_text,
                    current_quest_answer,
                )
                service_recovery_closing_node = create_question_node(
                    next_quest_id,
                    next_quest["quesText"],
                    next_quest["answer"],
                    skip_response=True,
                )
                satisfied_node = create_question_node(
                    satisfied_quest_id,
                    satisfied_quest_text,
                    satisfied_quest_answer,
                    skip_response=True,
                )

                # Moving from last question to Service Recovery Question
                edges.append(
                    {
                        "id": f"prevQuest{prev_quest_id}ToCurrentQuest{current_quest_id}",
                        "source": f"Question {prev_quest_id}",
                        "target": f"Question {current_quest_id}",
                        "label": "move here when the overall satisfaction of the survey was poor, not good, excellent, or anything else along those lines",
                    }
                )

                # Moving from Service Recovery Question to Service Recovery Closing
                edges.append(
                    {
                        "id": f"prevQuest{current_quest_id}ToCurrentQuest{next_quest_id}",
                        "source": f"Question {current_quest_id}",
                        "target": f"Question {next_quest_id}",
                        "label": "proceed",
                    }
                )

                # Moving from last question to Satisfied Closing
                edges.append(
                    {
                        "id": f"prevQuest{prev_quest_id}ToCurrentQuest{satisfied_quest_id}",
                        "source": f"Question {prev_quest_id}",
                        "target": f"Question {satisfied_quest_id}",
                        "label": "move here when the overall satisfaction of the survey was good, great, excellent",
                        "description": "Only move here when the survey's satisfaction was well received, the person enjoyed or anything else along those lines",
                    }
                )

                nodes.append(prev_node)
                nodes.append(service_recovery_quest_node)
                nodes.append(service_recovery_closing_node)
                nodes.append(satisfied_node)

                break

        else:

            # Only add the condition if the question has an answer
            extra_prompt_info = None
            if prev_quest_answer:
                extra_prompt_info = CLARIFYING_QUESTION_MAX_ATTEMPTS_PROMPT
            condition_example = QUESTION_WITH_ANSWER_CONDITION_EXAMPLE.format(
                quest_text=prev_quest_text, quest_answer=prev_quest_answer
            )

            prev_node = create_question_node(
                prev_quest_id,
                prev_quest_text,
                prev_quest_answer,
                extra_prompt_info=extra_prompt_info,
                condition=condition_example,
                total_questions=total_questions,
            )
        nodes.append(prev_node)

        # If the current question is affected by skip logic, create a webhook node for it
        if not all(pd.isna(current_quest_affected_data.answerId)):

            skip_logic_data = current_quest_affected_data.to_dict("records")
            answer_history = [
                {"id": ques_id, "ans_id": "{{answerID{ques_id}}}".replace("{ques_id}", f"{ques_id}")}
                for ques_id in range(1, current_quest_id)
            ]

            # If the node after the current question is not affected by skip logic, use its connection directly
            should_be_next_question = False
            if type(next_quest) == pd.Series:

                if all(pd.isna(next_quest_affected_data.answerId)):
                    should_be_next_question = True

            webhook_url = f"{SERVICE_BASE_URL}/skip_question"
            webhook_body = json.dumps(
                {
                    "question_id": int(current_quest_id),
                    "answer_history": answer_history,
                    "skip_logic": skip_logic_data,
                }
            )

            webhook_response_data = [
                {
                    "data": "$.proceed",
                    "name": "proceed_to_next_question",
                    "context": "",
                }
            ]
            webhook_response_pathways = [
                [
                    "proceed_to_next_question",
                    "==",
                    "true",
                    {
                        "id": f"Question {current_quest_id}",
                        "name": f"Question {current_quest_id}",
                    },
                ],
                [
                    "proceed_to_next_question",
                    "==",
                    "false",
                    {
                        "id": (
                            f"Question {next_quest_id}"
                            if should_be_next_question
                            else f"Question {current_quest_id} Webhook"
                        ),
                        "name": (
                            f"Question {next_quest_id}"
                            if should_be_next_question
                            else f"Question {current_quest_id} Webhook"
                        ),
                    },
                ],
            ]

            webhook_node = create_webhook_node(
                prev_quest_id, webhook_url, webhook_body, webhook_response_data, webhook_response_pathways
            )
            nodes.append(webhook_node)

            # Create an edge from the default node to the webhook node
            edges.append(
                {
                    "id": f"prevQuest{prev_quest_id}ToPrevQuestWebhook{prev_quest_id}",
                    "source": f"Question {prev_quest_id}",
                    "target": f"Question {prev_quest_id} Webhook",
                    "label": "proceed",
                }
            )
        else:

            edges.append(
                {
                    "id": f"prevQuest{prev_quest_id}ToCurrentQuest{current_quest_id}",
                    "source": f"Question {prev_quest_id}",
                    "target": f"Question {current_quest_id}",
                    "label": "proceed",
                }
            )

    return nodes, edges
