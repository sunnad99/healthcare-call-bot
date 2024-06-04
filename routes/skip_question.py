import pandas as pd

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from .route_params.generic import BadRequestResponse, UnauthorizedResponse

router = APIRouter()


@router.post(
    "/skip_question",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BadRequestResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
    },
)
async def skip_question(request: Request):

    payload = await request.json()

    skip_logic = payload["skip_logic"]
    answer_history = payload["answer_history"]
    quest_id = payload["question_id"]

    print("Answer history is: ", answer_history)

    skip_logic_df = pd.DataFrame(skip_logic)
    answer_history_df = pd.DataFrame(answer_history)

    half_answered_questions = answer_history_df[~answer_history_df.ans_id.isna()]
    all_answered_questions = half_answered_questions[~half_answered_questions.ans_id.str.contains("{{")].astype(
        {"ans_id": "Int64", "id": "Int64"}
    )

    filtered_data = skip_logic_df.merge(
        all_answered_questions, how="inner", left_on=["answerId", "questionId"], right_on=["ans_id", "id"]
    )

    # No match was found within the skip_logic...have to skip this question
    if filtered_data.empty:

        print(f"No skip logic found for question {quest_id}...proceeding to ask the question")

        return JSONResponse(status_code=status.HTTP_200_OK, content={"proceed": True})

    return JSONResponse(status_code=status.HTTP_200_OK, content={"proceed": False})
