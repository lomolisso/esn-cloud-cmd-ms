import os
from dotenv import load_dotenv

# Retrieve enviroment variables from .env file
load_dotenv()

SECRET_KEY: str = os.environ.get("SECRET_KEY")

REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB: int = int(os.environ.get("REDIS_DB", 0))

CLOUD_API_URL: str = os.environ.get("CLOUD_API_URL")

TIMEZONE: str = os.environ.get("TIMEZONE", "Chile/Continental")

ORIGINS: list = [
    "*"
]
