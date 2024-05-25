import uvicorn
from fastapi import FastAPI

from routes import get_surveyor_info

app = FastAPI()

app.include_router(get_surveyor_info.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)
