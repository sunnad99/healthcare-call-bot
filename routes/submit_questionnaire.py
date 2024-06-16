import datetime
import json
import requests
import pandas as pd

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from utils import get_user_details
from services.bland_ai.utils import extract_chosen_answer
from .route_params.generic import BadRequestResponse, UnauthorizedResponse

# from config import QUEST_SHEET, QUEST_SHEET_HEADERS # TODO: Uncomment it when done

router = APIRouter()


@router.post(
    "/questionnaire/submit",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BadRequestResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
    },
)
async def submit_questionnaire(request: Request):

    # NOTE: The format will be equivalent from the response of the GET Call API
    # https://docs.bland.ai/api-v1/get/calls-id

    payload = await request.body()
    call_vars = payload.get("variables")

    pathway_id = call_vars.get("pathway_id")
    pathway_name = call_vars.get("pathway_name")
    questionnaire = json.loads(call_vars.get("questionnaire"))
    call_id = call_vars.get("chcs_call_id")
    phone_number = call_vars.get("phone_number")

    # Obtaining the simple questionnaire data (for submission to CG OSMS)
    quest_simple = []
    for cur_quest in range(1, len(questionnaire) + 1):
        try:
            answer_id = call_vars[f"answerID{cur_quest}"]
            answer_text = call_vars[f"answerText{cur_quest}"]

            if type(answer_id) == str:
                answer_id = None

            quest_simple.append(
                {
                    "ansId": answer_id,
                    "sequence": cur_quest,
                    "uniqueId": "1",  # TODO: Generate SHA-1 hash
                    "callId": call_id,
                    "openEnded": None if answer_id else "N/A",
                }
            )
        except KeyError as e:
            print(f"No more answers to process...{cur_quest} answers processed")
            break
    quest_df = pd.DataFrame(questionnaire)
    quest_simple_df = pd.DataFrame(quest_simple)
    quest_simple_data = (
        quest_simple_df.merge(quest_df[["sequence", "projectId", "quesId"]], on="sequence")
        .astype({"ansId": "Int64"})
        .to_dict(orient="records")
    )

    # Formatting the full questionnaire data (For human readability)
    quest_full_df = quest_simple_df.merge(quest_df[["sequence", "quesText", "answer"]], on="sequence", how="left")[
        ["sequence", "ansId", "quesText", "answer"]
    ].rename(columns={"sequence": "id"})
    quest_full_df["chosenAnswer"] = quest_full_df.apply(extract_chosen_answer, axis=1)
    quest_full_data = quest_full_df.to_dict(orient="records")

    # Insert the headers if they don't exist
    if not QUEST_SHEET.get_all_values():
        QUEST_SHEET.insert_row(QUEST_SHEET_HEADERS, index=1)

    quest_spreadsheet_data = {
        "pathwayId": pathway_id,
        "pathwayName": pathway_name,
        "submissionQuestionnaire": quest_simple_data,
        "fullQuestionnaire": quest_full_data,
        "phoneNumber": phone_number,
        "receiveDate": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "callStatus": "incomplete",
        "submissionStatus": "incomplete",
    }

    # TODO: Make sure also that if the the necessary amount of questions are answered,
    # i.e. all the questions up to (and not including) the last question are answered and if the call dropped before the last question, the submission status should be "complete"
    if len(quest_simple) == len(questionnaire):
        print("The number of questions answered is equal to the number of questions in the questionnaire")
        quest_spreadsheet_data["callStatus"] = "complete"
        auth_token = get_user_details()
        url = "https://beta.api.cg-osms.com/call-survey"
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = requests.request("POST", url, headers=headers, json=payload)
        status_code = response.status_code
        if status_code == 200:
            quest_spreadsheet_data["submissionStatus"] = "complete"

    # Store the answers in a spreadsheet
    finalized_spreadsheet_data = [quest_spreadsheet_data.get(header, "") for header in QUEST_SHEET_HEADERS]
    QUEST_SHEET.append_row(finalized_spreadsheet_data)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Questionnaire stored successfully"},
    )
