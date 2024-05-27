import requests
import json

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse


from utils import get_user_details, range_calculator, get_fixed_question_id

from .route_params.generic import BadRequestResponse, UnauthorizedResponse
import pandas as pd

router = APIRouter()


def process_response(response_json):
    # Extract the questionnaire and logic dataframes and fix the question ids
    quest_df = pd.DataFrame(response_json["questionnaire"]).replace({pd.NA: None})
    logic_df = pd.DataFrame(response_json["logic"]).replace({pd.NA: None})

    ranges, non_questions_df = range_calculator(quest_df)
    actual_questions = len(quest_df) - len(non_questions_df)

    logic_df["questionId"] = logic_df.questionId.apply(get_fixed_question_id, args=(ranges,))
    logic_df["affectedQuestionId"] = logic_df.affectedQuestionId.apply(get_fixed_question_id, args=(ranges,))
    logic_df = logic_df.astype({"questionId": "Int64", "answerId": "Int64"})

    quest_dict, logic_dict = quest_df.to_dict(orient="records"), logic_df.to_dict(orient="records")

    return quest_dict, logic_dict, actual_questions


@router.get(
    "/questionnaire",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BadRequestResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
    },
)
async def get_questionnaire(project_id: int, surveyor_id: int):

    auth_token = get_user_details()

    url = "https://beta.api.cg-osms.com/questionnaire/logic"

    params = {"projectId": project_id, "surveyorId": surveyor_id, "languageId": 1}
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = requests.request("GET", url, headers=headers, params=params)
    status_code = response.status_code

    if status_code == 400:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid project id or surveyor id", "status_code": status_code},
        )
    elif status_code == 401:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": f"Unauthorized access for project_id {project_id} and surveyor_id {surveyor_id}",
                "status_code": status_code,
            },
        )

    response_json = response.json()
    questionnaire, logic, total_questions = process_response(response_json)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "questionnaire": questionnaire,
            "logic": logic,
            "total_questions": total_questions,
        },
    )
