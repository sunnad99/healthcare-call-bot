import requests


from fastapi import APIRouter, status
from fastapi.responses import JSONResponse


from utils import get_user_details

from .route_params.generic import BadRequestResponse, UnauthorizedResponse

router = APIRouter()


@router.get(
    "/calls",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BadRequestResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
    },
)
async def get_calls(project_id: int, surveyor_id: int):

    auth_token = get_user_details()

    url = "https://beta.api.cg-osms.com/calls"

    payload = {"projectId": str(project_id), "surveyorId": surveyor_id}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }

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
                "error": f"Unauthorized access for project_id {project_id} and surveyor_id {surveyor_id}",
                "status_code": status_code,
            },
        )

    response_json = response.json()

    return response_json
