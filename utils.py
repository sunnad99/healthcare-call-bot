import requests

import pandas as pd
from credentials import EMAIL, PASSWORD, USER_KEY


def get_user_details(jwt: bool = True) -> str or dict:
    """
    Get the user details from the API. If jwt is True,
    return the JWT token. If False, return the user details. Default is True.

    Args:
        jwt (bool) default -> True: Boolean to return the JWT token or the user details

    Returns:
        str or dict: The JWT token or the user details
    """

    url = "https://beta.api.cg-osms.com/sessions"

    payload = {
        "email": EMAIL,
        "password": PASSWORD,
        "userKey": USER_KEY,
        "isRemember": True,
    }

    response = requests.request("POST", url, json=payload)
    response.raise_for_status()

    response_json = response.json()
    data = response_json["user"]
    if jwt:
        data = response_json["accessToken"]

    return data


def range_calculator(quest_df: pd.DataFrame) -> tuple:
    """
    Calculate the ranges of non-question indices in the quest_df DataFrame.

    Args:
        quest_df (pd.DataFrame): DataFrame containing the questionnaire data.

    Returns:
        tuple: A tuple containing the ranges and the non_questions_df DataFrame.

    Raises:
        ValueError: If quest_df is empty or does not contain the required columns.

    """
    if quest_df.empty:
        raise ValueError("quest_df must not be empty")

    non_questions_df = quest_df[quest_df.ansId.isin([[]])].reset_index(names="range_index")
    non_questions_df.range_index = non_questions_df.range_index + 1

    non_question_count = 1
    ranges = []
    total_questions = len(quest_df)
    prev_record, cur_record, cur_range_record = non_questions_df.iloc[0], None, None
    for i in range(1, len(non_questions_df)):

        cur_record = non_questions_df.iloc[i]
        prev_range_index, cur_range_index = prev_record.range_index, cur_record.range_index
        if cur_range_index - prev_range_index > 1:

            start, end = prev_range_index + 1, cur_range_index - 1
            ranges.append({"start": start, "end": end, "non_question_count": non_question_count})

            # Reset count and update cur_range_record
            non_question_count = 0
            cur_range_record = cur_record

        prev_record = cur_record
        non_question_count += 1

    if total_questions > cur_record.range_index:
        ranges.append(
            {
                "start": cur_range_record.range_index + 1,
                "end": total_questions,
                "non_question_count": non_question_count,
            }
        )

    return ranges, non_questions_df


def get_fixed_question_id(question_id, ranges):

    if pd.isna(question_id):
        return None

    accumlated_count = 0
    for range_ in ranges:

        count = range_["non_question_count"]
        accumlated_count += count
        start, end = range_["start"], range_["end"]
        if question_id >= start and question_id <= end:
            return question_id - accumlated_count

    return question_id
