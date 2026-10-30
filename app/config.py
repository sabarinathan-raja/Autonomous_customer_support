
import os

from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

APP_NAME = os.getenv(
    "APP_NAME",
    "Autonomous Customer Support and Escalation System",
)

APP_ENV = os.getenv("APP_ENV", "development")

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
