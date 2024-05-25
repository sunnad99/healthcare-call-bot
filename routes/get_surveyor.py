from fastapi import APIRouter
from pydantic import BaseModel

from utils import get_user_details


router = APIRouter()


class SurveyorInfoResponse(BaseModel):
    email: str
    firstName: str
    id: int
    isActive: bool
    isDeleted: bool
    lastName: str
    phoneNumber: str
    role: int


@router.get("/surveyor", response_model=SurveyorInfoResponse)
async def get_surveyor():

    user_info = get_user_details(jwt=False)

    return user_info
