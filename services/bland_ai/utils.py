import re

from .config import QUESTION_PROMPT, ANSWER_TEMPLATE


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


def create_question_node(quest_id: int, quest_text: str, quest_answer: list[dict]) -> dict:

    node = {
        "id": f"Question {quest_id}",
        "type": "Default",
        "data": {
            "name": f"Question {quest_id}",
            "prompt": QUESTION_PROMPT.format(quest_text=quest_text, quest_answer=quest_answer),
            "extractVars": [
                [
                    ANSWER_TEMPLATE["name"].format(question_num=quest_id),
                    ANSWER_TEMPLATE["type"],
                    ANSWER_TEMPLATE["value"].format(answers=quest_answer if quest_answer else "null"),
                ]
            ],
        },
    }

    if quest_id == 1:
        node["data"]["isStart"] = True
    else:
        node["data"]["isStart"] = False

    return node


def create_webhook_node(
    quest_id: int, url: str, body: str, response_data: list[dict] = None, response_pathways: list[list] = None
) -> dict:

    node = {
        "id": f"Question {quest_id} Webhook",
        "type": "Webhook",
        "data": {
            "name": f"Question {quest_id} Webhook",
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

    if response_data:
        node["data"]["responseData"] = response_data

    if response_pathways:
        node["data"]["responsePathways"] = response_pathways

    return node
