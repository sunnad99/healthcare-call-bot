import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import get_surveyor, get_survey, get_calls, get_questionnaire, submit_questionnaire

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

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
