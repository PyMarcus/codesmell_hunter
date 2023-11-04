import asyncio
import json
import re
import sys
import time
import typing
from typing import Tuple

import httpx
from bs4 import BeautifulSoup
from httpx import Response

from app.models.bad_smell import BadSmell
from app.models.source_code_smell import SourceCodeSmell
from app.package.register import LogMaker
from app.repository.database import DataBase
from app.service.api_gpt_request import APIGPTRequest


class BaseLinksCodeDownload:
    def __init__(self, question: str) -> None:
        self.__question: str = question
        self.__request_interval: float = 0.02
        self.__request_interval_after_error: float = 0.05
        self.__success: int = 200
        self.__gpt: APIGPTRequest = APIGPTRequest()

    async def __http_request(self, link: str) -> Response:
        async with httpx.AsyncClient() as client:
            code = await client.get(link)
            return code

    def __parser(self, code: Response, start_line: int, end_line: int) -> str | Response:
        if code.status_code == self.__success:
            parse = BeautifulSoup(code.text, "html.parser")
            code_content = json.loads(parse.text)["payload"]["blob"]["rawLines"]
            lines_expected = code_content[start_line - 1:end_line]
            return lines_expected
        return code

    def __regex(self, text: str) -> str:
        content = text.split("the bad smells are:")
        try:
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
        for row in source_code:
            code = await self.__http_request(row.link)
            code_from_html: str | Response = self.__parser(code, row.start_line, row.end_line)
            if code_from_html is None:
                LogMaker.write_log(f"Fail to get {row.link} -"
                                   f" status_code {code_from_html.status_code}", "error")
                time.sleep(self.__request_interval_after_error)
                continue
            gpt_response = self.__gpt.gpt_response(self.__question)
            gpt_parser, found = self.__gpt_response_parser(gpt_response)
            bad_smell: BadSmell = BadSmell(
                id_source_code=row.id,
                chat_gpt_response=gpt_response,
                question=self.__question,
                bad_smell_base=row.smell,
                bad_smell_gpt=gpt_parser,
                found_any=found,
                valid_bad_smell=None,
                bad_smell_in_base=True,
                bad_smell_not_in_base=', '.join([smell for smell in gpt_parser if smell not in row.smell]),
                bad_smell_not_found=','.join([smell for smell in [row.smell] if smell not in gpt_parser]),
                index=None,
                index_base=row.id_base,
                url_github=row.link
            )
            DataBase.insert_bad_smell(bad_smell)
            time.sleep(self.__request_interval)
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
