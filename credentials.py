import os
from dotenv import load_dotenv

load_dotenv()

# Get the environment variables
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
USER_KEY = os.getenv("USER_KEY")
