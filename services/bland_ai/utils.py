import re

import pandas as pd

from .config import (
    ANSWER_ID_TEMPLATE,
    ANSWER_TEXT_TEMPLATE,
    QUESTION_WITH_ANSWERS_PROMPT,
    QUESTION_WITHOUT_ANSWERS_PROMPT,
)


## Bland.ai utility functions
def fill_placeholders(row, caller_data):

    question = row["quesText"]
    visit_infos = caller_data["visitInfos"]

    special_placeholders_to_replace = {
        "Provider Name": caller_data.get("provider", ""),
        "Site": caller_data.get("center", ""),
    }

    placeholders = re.findall(r"<<([^<>]+)>>", question)
    for placeholder in placeholders:

        filtered_dynamic_data = list(filter(lambda x: x["field"] == placeholder, visit_infos))

        if filtered_dynamic_data:
            question = question.replace(f"<<{placeholder}>>", filtered_dynamic_data[0]["value"])
        elif placeholder in special_placeholders_to_replace:
            question = question.replace(f"<<{placeholder}>>", special_placeholders_to_replace[placeholder])
    return question


def extract_chosen_answer(row):

    ans_id = row["ansId"]
    ans_list = row["answer"]
    if pd.isna(ans_id):
        return None

    filtered_answer = list(filter(lambda x: x["id"] == ans_id, ans_list))
    if not filtered_answer:
        return None

    answer = filtered_answer[0]["title"]
    return answer


def create_question_node(
    quest_id: int,
    quest_text: str,
    quest_answer: list[dict],
    extra_prompt_info: str = None,
    condition: str = None,
    skip_response: bool = False,
    total_questions: int = None,
) -> dict:

    quest_prompt = quest_prompt = QUESTION_WITHOUT_ANSWERS_PROMPT.format(quest_text=quest_text)
    if quest_answer:
        quest_prompt = QUESTION_WITH_ANSWERS_PROMPT.format(
            quest_text=quest_text, quest_answer=quest_answer, total_questions=total_questions, question_num=quest_id
        )

    if extra_prompt_info:
        quest_prompt += extra_prompt_info

    node = {
        "id": f"Question {quest_id}",
        "type": "Default",
        "data": {
            "isStart": True if quest_id == 1 else False,
            "name": f"Question {quest_id}",
            "prompt": quest_prompt,
            "extractVars": [
                [
                    ANSWER_ID_TEMPLATE["name"].format(question_num=quest_id),
                    ANSWER_ID_TEMPLATE["type"],
                    ANSWER_ID_TEMPLATE["value"].replace("{answers}", str(quest_answer) if quest_answer else "null"),
                ],
                [
                    ANSWER_TEXT_TEMPLATE["name"].format(question_num=quest_id),
                    ANSWER_TEXT_TEMPLATE["type"],
                    ANSWER_TEXT_TEMPLATE["value"],
                ],
            ],
        },
    }

    if condition:
        node["data"]["condition"] = condition

    if skip_response:
        node["data"]["modelOptions"] = {
            "modelType": "smart",
            "temperature": 0.2,
            "skipUserResponse": skip_response,
        }

    return node


def create_webhook_node(
    quest_id: int,
    url: str,
    body: str,
    response_data: list[dict] = None,
    response_pathways: list[list] = None,
    quest_name: str = None,
    prompt: str = None,
) -> dict:

    name = f"Question {quest_id} Webhook"
    if quest_name:
        name = quest_name
    node = {
        "id": name,
        "type": "Webhook",
        "data": {
            "name": name,
            "isStart": False,
            "url": url,
            "body": body,
            "method": "POST",
            "timeoutValue": 3600,
            "modelOptions": {
                "modelType": "smart",
                "temperature": 0.2,
                "skipUserResponse": True,
            },
        },
    }

    if prompt:
        node["data"]["prompt"] = prompt

    if response_data:
        node["data"]["responseData"] = response_data

    if response_pathways:
        node["data"]["responsePathways"] = response_pathways

    return node
