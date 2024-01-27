import os

from dotenv import load_dotenv

path: str = os.path.abspath(os.path.join(os.path.abspath("."), ".env"))
print(path)
load_dotenv(path)

HOST: str = os.getenv("host")
DATABASE: str = os.getenv("database")
PASSWORD: str = os.getenv("password")
NAME: str = os.getenv("user")
PORT: int = int(os.getenv("port"))\
    if os.getenv("port") is not NAME else os.getenv("port")
GPT_KEY: str = os.getenv("gpt_key")
