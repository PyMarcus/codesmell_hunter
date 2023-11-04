import time

import openai

from app.constants.env import GPT_KEY


class APIGPTRequest:
    def __init__(self) -> None:
        self.__TOKEN: str = GPT_KEY
        self.__response = []
        self.__model: str = "gpt-3.5-turbo-instruct"
        self.__max_tokens: int = 1000
        self.__interval: float = 0.5

    def __request(self, question: str) -> str:
        try:
            openai.api_key = self.__TOKEN
            response = openai.Completion.create(
                model=self.__model,
                prompt=question,
                max_tokens=self.__max_tokens
            )
            print(response)
            time.sleep(self.__interval)
            return response["choices"][0]["text"]
        except Exception as e:
            return f"Fail to connect: {e}"

    def gpt_response(self, question: str) -> str:
        return self.__request(question)
