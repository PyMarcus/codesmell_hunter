import asyncio
import json
import sys
import time
import typing
import httpx
from bs4 import BeautifulSoup
from transformers import BertTokenizer
from httpx import Response
from app.models.bad_smell import BadSmell
from app.models.source_code_smell import SourceCodeSmell
from app.package.register import LogMaker
from app.repository.database import DataBase
from app.service.api_gpt_request import APIGPTRequest


class BaseLinksCodeDownload:
    """
       This class handles the download and analysis of source code files from GitHub links.
       It interacts with the GPT API to analyze the code for specific code smells.

       Args:
           question (str): The question or prompt to be used for GPT API queries.
           limit_tokens (bool, optional): Whether to limit the token count in the generated prompt.
                                          Defaults to True.

       Methods:
           __http_request(link: str) -> Response: Sends an HTTP GET request to the provided link.
           __count_tokens(question: str) -> int: Counts the number of tokens in a given text.
           __parser(code: Response, start_line: int, end_line: int) -> str | Response: Parses raw code response.
           __regex(text: str) -> str: Extracts relevant information from GPT API response.
           __gpt_response_parser(gpt_response: str) -> Tuple[str, bool]: Parses GP API response.
           __code_download() -> None: Downloads and analyzes source code from GitHub links.
           start() -> None: Initiates the code download and analysis process.
       """
    def __init__(self, question: str, limit_tokens: bool = True) -> None:
        self.__question: str = question
        self.__request_interval: float = 0.02
        self.__request_interval_after_error: float = 0.05
        self.__success: int = 200
        self.__gpt: APIGPTRequest = APIGPTRequest()
        self.__limit_tokens = limit_tokens
        if limit_tokens:
            self.__tokens = 4097

    async def __http_request(self, link: str) -> Response:
        async with httpx.AsyncClient() as client:
            code = await client.get(link)
            return code

    def __count_tokens(self, question: str) -> int:
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        tokens = tokenizer.tokenize(tokenizer.decode(tokenizer.encode(question)))
        num_tokens = len(tokens)
        return num_tokens

    def __parser(self, code: Response, start_line: int, end_line: int) -> str | Response:
        if code.status_code == self.__success:
            parse = BeautifulSoup(code.text, "html.parser")
            code_content = json.loads(parse.text)["payload"]["blob"]["rawLines"]
            lines_expected = code_content[start_line - 1:end_line]
            return lines_expected
        return code

    def __regex(self, text: str) -> str:
        try:
            content = text.split("1")
            return content[1]
        except:
            return ""

    def __gpt_response_parser(self, gpt_response: str) -> typing.Tuple[str, bool]:
        gpt_response = gpt_response
        parser = self.__regex(gpt_response)
        if "YES" in gpt_response:
            return parser, True
        return parser, False

    async def __code_download(self) -> None:
        source_code: typing.List[typing.Type[SourceCodeSmell]] = DataBase.select_all_source_code_smell()
        i = 0
        for row in source_code:
            code = await self.__http_request(row.link)
            code_from_html: str | Response = self.__parser(code, row.start_line, row.end_line)
            if code_from_html is None:
                LogMaker.write_log(f"Fail to get {row.link} -"
                                   f" status_code {code_from_html.status_code}", "error")
                time.sleep(self.__request_interval_after_error)
                continue

            question = self.__question + ":\n" + ' '.join(code_from_html)

            if self.__limit_tokens:
                if self.__count_tokens(question) >= self.__tokens:
                    LogMaker.write_log(f"Maximum context length tokens exceded to {row.link}", "warning")
                    continue

            gpt_response = self.__gpt.gpt_response(question)
            if not gpt_response:
                LogMaker.write_log(f"Fail to get response for {row.link} - {row.id_base}", "error")
            gpt_parser, found = self.__gpt_response_parser(gpt_response)
            bad_smell: BadSmell = BadSmell(
                id_source_code=row.id,
                chat_gpt_response=gpt_response.replace("\n", " "),
                question=question,
                badsmell_base=row.smell,
                bad_smell_gpt=gpt_parser.replace("\n", "").replace(".", ""),
                found_any=found,
                valid_bad_smell=None,
                bad_smell_in_base=True if row.smell in gpt_parser.lower() else False,
                bad_smell_not_in_the_base=', '.join([smell.replace("\n", "") for smell in gpt_parser.split(',') if row.smell not in smell.lower()]),
                bad_smell_not_found=','.join([smell for smell in [row.smell] if smell not in gpt_parser.lower()]),
                index=None,
                index_base=row.id_base,
                url_github=row.link
            )
            DataBase.insert_bad_smell(bad_smell)
            time.sleep(self.__request_interval)
            i += 1
            if i == 100:
                sys.exit(0)

    def start(self) -> None:
        # path: str = os.path.join(os.path.abspath(os.path.pardir), "downloaded")
        # if not os.path.exists(path):
        #    LogMaker.write_log(f"Creating {path}", "info")
        #    os.mkdir(path)
        # time.sleep(2)
        start = time.time()
        LogMaker.write_log("Accessing github codes...", "info")
        asyncio.run(self.__code_download())
        end = time.time()
        LogMaker.write_log(f"Complete {end - start:.2f}", "info")
