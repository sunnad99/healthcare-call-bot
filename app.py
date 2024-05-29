import uvicorn
from fastapi import FastAPI

from routes import get_surveyor, get_survey, get_calls, get_questionnaire, submit_questionnaire

app = FastAPI()

app.include_router(get_surveyor.router)
app.include_router(get_survey.router)
app.include_router(get_calls.router)
app.include_router(get_questionnaire.router)
app.include_router(submit_questionnaire.router)


@app.head("/health")
async def health():
    return {"message": "API is healthy."}


@app.get("/")
def read_root():
    return {"message": "Welcome to CG-OSMS API."}


if __name__ == "__main__":
    uvicorn.run(app, port="8000")
