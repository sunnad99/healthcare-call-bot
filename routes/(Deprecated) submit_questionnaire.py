import requests
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


from utils import get_user_details
from .route_params.generic import BadRequestResponse, UnauthorizedResponse

router = APIRouter()


class Answer(BaseModel):
    quesId: int
    ansId: None or int
    sequence: int
    uniqueId: str
    callId: int
    openEnded: None or str  # None if ansId else "N/A" TODO: check this
    projectId: int


class SubmitQuestionnaireInput(BaseModel):
    survey: list[Answer]
    isPut: bool = False
    questionnaire: str
    pathway_id: str


@router.post(
    "/questionnaire",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BadRequestResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
    },
)
async def submit_questionnaire(request_body: SubmitQuestionnaireInput):

    payload = request_body.dict()

    # TODO: Make sure the payload doesn't have answers with no answer Ids
    # TODO: Pass in the pathway-id as well in here

    auth_token = get_user_details()
    url = "https://beta.api.cg-osms.com/call-survey"
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = requests.request("POST", url, headers=headers, json=payload)
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
                "error": f"Unauthorized access!",
                "status_code": status_code,
            },
        )

    call_id = payload[0]["callId"]
    project_id = payload[0]["projectId"]

    # TODO: Delete the previously created pathway using the pathway id

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Questionnaire submitted successfully", "callId": call_id, "projectId": project_id},
    )
