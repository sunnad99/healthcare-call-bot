import requests
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
