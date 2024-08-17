import os
import gspread

from dotenv import load_dotenv

load_dotenv()

SERVICE_BASE_URL = os.getenv("SERVICE_BASE_URL", "http://localhost:8000")


########################## CLIENTS ##########################
# Google Sheet client
SHEET_ID = os.getenv("GSPREAD_SHEET_ID")
GSPREAD_SECRET_FILE = os.getenv("GSPREAD_SECRET_FILE")
GSPREAD_CLIENT = gspread.service_account(filename=GSPREAD_SECRET_FILE)

QUEST_SHEET_NAME = "Sheet1"
SPREAD_SHEET = GSPREAD_CLIENT.open_by_key(SHEET_ID)
QUEST_SHEET = SPREAD_SHEET.worksheet(QUEST_SHEET_NAME)
QUEST_SHEET_HEADERS = [
    "pathwayId",
    "pathwayName",
    "submissionQuestionnaire",
    "fullQuestionnaire",
    "phoneNumber",
    "receiveDate",
    "callStatus",
    "submissionStatus",
]
