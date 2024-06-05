import json
import pandas as pd

from .utils import create_question_node, create_webhook_node, fill_placeholders
from config import BASE_URL


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
        filtered_lang_questions_df[["id", "quesText"]], left_on="quesId", right_on="id", how="left"
    ).drop(columns=["question", "id"])

    return quest_with_text_df


def create_nodes_and_edges(
    quest_with_text_df: pd.DataFrame, caller_data: dict, skip_logic: dict, pathway_id: str
) -> tuple:

    nodes, edges, current_quest = [], [], None
    caller_id, project_id = caller_data["callId"], caller_data["projectId"]
    skip_logic_df = pd.DataFrame(skip_logic).astype({"questionId": "Int64", "answerId": "Int64"})
    for index in range(1, len(quest_with_text_df)):

        prev_quest, current_quest, next_quest = (
            quest_with_text_df.iloc[index - 1],
            quest_with_text_df.iloc[index],
            None,
        )

        prev_quest_id = prev_quest["sequence"]
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

        prev_node = create_question_node(prev_quest_id, prev_quest_text, prev_quest_answer)
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

            webhook_url = f"{BASE_URL}/skip_question"
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

        # Adding the last node
        if index == len(quest_with_text_df) - 1:

            last_node = create_question_node(current_quest_id, current_quest_text, current_quest_answer)
            nodes.append(last_node)

    # Create the webhook node for submitting the questionnaire
    submission_webhook_url = f"{BASE_URL}/submit_questionnaire"
    submission_webhook_body = json.dumps(
        {
            "pathway_id": pathway_id,
            "survey": [
                {
                    "ansId": "{{answerID{ques_id}}}".replace("{ques_id}", f"{quest_id}"),
                    "quesId": int(quest_with_text_df.iloc[quest_id - 1].quesId),
                    "sequence": quest_id,
                    "uniqueId": "b616d37750034658a930196ad0fbccd851158e42fb83478195",  # TODO: Generate a unique id using SHA-1
                    "callId": caller_id,
                    "openEnded": None,
                    "projectId": project_id,
                }
                for quest_id in range(1, len(quest_with_text_df) + 1)
            ],
            "isPut": False,
        }
    )
    submission_webhook_node = create_webhook_node(current_quest_id, submission_webhook_url, submission_webhook_body)
    nodes.append(submission_webhook_node)

    return nodes, edges
