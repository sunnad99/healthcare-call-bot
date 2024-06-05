import requests
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from credentials import BLAND_API_KEY
from services.bland_ai.main import (
    create_nodes_and_edges,
    extract_answers,
    extract_questionnaire_text,
)

from .route_params.generic import BadRequestResponse, UnauthorizedResponse

router = APIRouter()


class SendCallInput(BaseModel):
    quest_data: dict
    caller_data: dict


@router.post(
    "/send_call",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BadRequestResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
    },
)
async def send_call(request_body: SendCallInput):

    payload = request_body.dict()
    quest_data = payload["quest_data"]
    caller_data = payload["caller_data"]
    skip_logic = quest_data["logic"]
    patient_lang_id = caller_data["languageId"]

    # Fill all the placeholders in the questionnaire and format the answers array
    print("Extracting questionnaire question and answer data...")
    quest_with_text_df = extract_questionnaire_text(quest_data, caller_data, lang_id=1)
    quest_with_text_df["answer"] = quest_with_text_df.apply(
        extract_answers,
        args=(patient_lang_id,),
        axis=1,
    )
    print("Questionnaire question and answer data extracted successfully...")
    # Create the pathway

    print("Creating pathway...")
    url = "https://api.bland.ai/v1/convo_pathway/create"
    project_id, call_id, patient_name, center, provider, phone_number = (
        caller_data["projectId"],
        caller_data["callId"],
        caller_data["visitorName"],
        caller_data["center"],
        caller_data["provider"],
        caller_data["phoneCell"] if caller_data.get("phoneCell") else caller_data.get("phoneHome"),
    )
    pathway_name = f"{project_id} - {call_id} - {patient_name} - {center} - {provider}"
    payload = {"name": pathway_name}
    headers = {
        "Authorization": BLAND_API_KEY,
        "Content-Type": "application/json",
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    status_code = response.status_code
    if status_code != 200:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Error creating pathway"},
        )
    response_json = response.json()
    status_msg = response_json["status"]
    if status_msg != "success":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Error creating pathway...there was an issue with the request"},
        )
    print("Pathway created successfully...")

    # Update the pathway
    print("Updating pathway...")
    pathway_id = response_json["pathway_id"]
    url = f"https://api.bland.ai/v1/convo_pathway/{pathway_id}"
    nodes, edges = create_nodes_and_edges(quest_with_text_df, caller_data, skip_logic=skip_logic, pathway_id=pathway_id)
    payload = {"name": pathway_name, "nodes": nodes, "edges": edges}
    headers = {
        "Authorization": BLAND_API_KEY,
        "Content-Type": "application/json",
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    status_code = response.status_code
    if status_code != 200:
        print(f"Error updating pathway...something went wrong {response.text}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Error updating pathway...something went wrong", "nodes": nodes, "edges": edges},
        )
    response_json = response.json()
    status_msg = response_json["status"]
    if status_msg != "success":
        print(f"Error updating pathway...there was an issue with the request {response.text}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Error creating pathway...there was an issue with the request"},
        )
    print("Pathway updated successfully...")
    # TODO: Make a call to the send call API

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Call successfully made to the client",
            "nodes": nodes,
            "edges": edges,
            "pathway_id": pathway_id,
        },
    )
