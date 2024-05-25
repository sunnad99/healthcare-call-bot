from pydantic import BaseModel


class BadRequestResponse(BaseModel):
    error: str
    status_code: int = 400
