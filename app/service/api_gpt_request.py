import sys
import time
import openai
from openai import OpenAI
from app.models import ErrorLog
from app.models import SourceCodeToQuery
from app.package.register import LogMaker
from app.constants.env import GPT_KEY
from app.repository.database import DataBase


class APIGPTRequest:
    def __init__(self) -> None:
        self.__TOKEN: str = GPT_KEY
        self.__response = []
        self.__model: str = "gpt-3.5-turbo-0125"
        self.__max_tokens: int = 1000
        self.__interval: float = 0.05

    def __request(self, question: str, row_id: int) -> str | None:
        try:
            # openai.api_key = self.__TOKEN
            client = OpenAI(api_key=self.__TOKEN)
            response = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                        {"role": "user", "content": question}
                    ]
                    )
            print(response.choices[0].message.content)
            time.sleep(self.__interval)
            return response.choices[0].message.content
        except Exception as e:
            error_log = ErrorLog(id_source_code=row_id,
                                 ds_error=f"ERROR QUERYING GPT FROM OPENAI: {e}")
            DataBase.insert_error_log(error_log)
            LogMaker.write_log(str(e), "error")
            sctq = SourceCodeToQuery(id_source_code=row_id, ds_source_code=question)
            DataBase.insert_source_to_query(sctq)
            DataBase.update_source_code_smell(row_id, 5)
            return None

    def gpt_response(self, question: str, row_id: int) -> str | None:
        return self.__request(question, row_id)


if __name__ == '__main__':
    x = APIGPTRequest()
    x.gpt_response("olá", -1)
