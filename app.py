import uvicorn
from fastapi import FastAPI

from routes import get_surveyor, get_calls, get_questionnaire

app = FastAPI()

app.include_router(get_surveyor.router)
app.include_router(get_calls.router)
app.include_router(get_questionnaire.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)
