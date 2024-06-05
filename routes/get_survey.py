import requests
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from utils import get_user_details
from .route_params.generic import BadRequestResponse, UnauthorizedResponse

router = APIRouter()


@router.get(
    "/survey",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BadRequestResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
    },
)
async def get_survey(surveyor_id: int):

    auth_token = get_user_details()

    url = "https://beta.api.cg-osms.com/projects/surveyors"
    params = {"surveyorId": surveyor_id, "skip": 0, "limit": 10, "orderBy": "name", "orderDir": "ASC"}
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
                "error": f"Unauthorized access!",
                "status_code": status_code,
            },
        )

    response_json = response.json()

    count = response_json["count"]
    data = response_json["rows"]

    # If no survey found for the surveyor, return a message.
    if count == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No survey found for the surveyor."},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data[0],
    )
