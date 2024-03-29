import asyncio
import json
import re
import sys
import time
import typing
import httpx
from bs4 import BeautifulSoup
from transformers import BertTokenizer
from httpx import Response
from app.models import SourceCodeToQuery
from app.models.bad_smell import BadSmell
# from app.models.source_code_smell import SourceCodeSmell
from app.models.pending_source_code_with_duplicates import PendingSourceCodeWithDuplicates
from app.models.error_log import ErrorLog
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
                                          Defaults to True.[ *FALSE if do u use GPT plus*]
          limit_rows (int, optional): Whether to limit the rows to insert in database.
                                          Defaults to 15000.

       Methods:
           __http_request(link: str) -> Response: Sends an HTTP GET request to the provided link.
           __count_tokens(question: str) -> int: Counts the number of tokens in a given text.
           __parser(code: Response, start_line: int, end_line: int) -> str | Response: Parses raw code response.
           __regex(text: str) -> str: Extracts relevant information from GPT API response.
           __gpt_response_parser(gpt_response: str) -> Tuple[str, bool]: Parses GP API response.
           __code_download() -> None: Downloads and analyzes source code from GitHub links.
           start() -> None: Initiates the code download and analysis process.
       """
    def __init__(self, question: str, limit_tokens: bool = True, limit_rows: int = 15000, question_number: int = 1) -> None:
        print(f"QUESTION NUMBER {question_number}")
        self.__question: str = question
        self.__request_interval: float = 0.02
        self.__request_interval_after_error: float = 0.05
        self.__success: int = 200
        self.__gpt: APIGPTRequest = APIGPTRequest()
        self.__limit_tokens = limit_tokens
        self.__limit = limit_rows
        if limit_tokens:
            self.__tokens = 16385
        # self.__source_code: typing.List[typing.Type[SourceCodeSmell]] = DataBase.select_all_source_code_smell()
        self.__source_code: typing.List[typing.Type[PendingSourceCodeWithDuplicates]] =\
            DataBase.select_all_pending_source_code_with_duplicates(0)
        self.__question_number = question_number

    async def __http_request(self, link: str, row_id: int) -> Response:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36'
        }
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            try:
                code = await client.get(link, follow_redirects=True)
                return code
            except httpx.ConnectError as err:
                LogMaker.write_log(f"Error: {err} to try access github link: {link}", "error")
                error_log = ErrorLog(id_source_code=row_id, ds_error=f"ERROR OF HTTP CONNECTION: {err}")
                DataBase.insert_error_log(error_log)
                DataBase.update_source_code_smell(row_id, 6)
                time.sleep(20)
                code = await client.get(link, follow_redirects=True)
                return code

    def __count_tokens(self, question: str) -> int:
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        tokens = tokenizer.tokenize(tokenizer.decode(tokenizer.encode(question)))
        num_tokens = len(tokens)
        return num_tokens

    def __parser(self, code: Response, start_line: int, end_line: int) -> typing.List[str] | Response:
        if code.status_code == self.__success:
            try:
                parse = BeautifulSoup(code.text, "html.parser")
                code_content = json.loads(parse.text)["payload"]["blob"]["rawLines"]
                try:
                    lines_expected = code_content[start_line - 1: end_line]
                    return lines_expected
                except TypeError as e:
                    LogMaker.write_log(f"Error to get lines expected: {e} to try parse: {code}", "error")
                    return code_content
            except Exception as e:
                LogMaker.write_log(f"Error to try parser code {code.text} - error {e}", "error")
                return code
        return code

    def __regex(self, text: str) -> str:
        regex_list = [
            r'"\w*smells?":\s*(\[[^\]]*\])',
            r'"\w*bad_smells":\s*(\[[^\]]*\])',
            r'"\w*the bad smells are":\s*(\[[^\]]*\])',
            r'"\w*bad smells are":\s*(\[[^\]]*\])',
            r'"\w*detected_bad_smells":\s*(\[[^\]]*\])'
        ]
        for regex in regex_list:
            match = re.search(regex, text)
            if match:
                bad_smells_list = match.group(1)
                bad_smells = re.findall(r'"([^"]+)"', bad_smells_list)
                return ', '.join(bad_smells)

        return ''

    def __gpt_response_parser(self, gpt_response: str, row: typing.Any) -> typing.Tuple[str, bool]:
        parser = self.__regex(gpt_response)
        if not parser:
            LogMaker.write_log(f"(REGEX GPT RESPONSE ERROR - but, keep going...) Error to get {row.link} ", "error")
            DataBase.update_source_code_smell(row.id, 12)
            error_log = ErrorLog(id_source_code=row.id, ds_error="GPT RESPONSE REGEX ERROR")
            DataBase.insert_error_log(error_log)
        if "YES" in gpt_response or "Yes" in gpt_response or "yes" in gpt_response:
            return parser, True
        LogMaker.write_log(f"(REGEX GPT RESPONSE ERROR - but, keep going...) Error to get {row.link} ", "error")
        DataBase.update_source_code_smell(row.id, 12)
        error_log = ErrorLog(id_source_code=row.id, ds_error="GPT RESPONSE REGEX ERROR")
        DataBase.insert_error_log(error_log)
        return parser, False

    async def __code_download(self) -> None:
        size = len(self.__source_code)
        LogMaker.write_log(f"PENDING SOURCE CODE LENGTH: {size}", "info")
        time.sleep(2)
        row = None
        offset = 0
        while True:
            try:
                self.__source_code = DataBase.select_all_pending_source_code_with_duplicates(offset=offset)
            except Exception as err:
                LogMaker.write_log(f"DATABASE RESPONSE ERROR - {row.link} ", "error")
                DataBase.update_source_code_smell(row.id, 7)
                error_log = ErrorLog(id_source_code=row.id, ds_error=err)
                DataBase.insert_error_log(error_log)
                continue
            offset += 300

            if not self.__source_code:
                break

            for index, row in enumerate(self.__source_code):
                if index >= size:
                    LogMaker.write_log(f"Forced {index} {size}", "warning")
                    break
                code = await self.__http_request(row.link, row.id)
                code_from_html: typing.List[str] | Response = self.__parser(code, row.start_line, row.end_line)
                if isinstance(code_from_html, Response):
                    time.sleep(self.__request_interval_after_error)
                    if code_from_html.status_code == 200:
                        LogMaker.write_log(f"(PARSER ERROR) Error to get {row.link} -"
                                           f" status_code {code_from_html.status_code}", "error")
                        DataBase.update_source_code_smell(row.id, 9)
                        error_log = ErrorLog(id_source_code=row.id, ds_error="PARSER ERROR")
                    else:
                        LogMaker.write_log(f"Error to get {row.link} -"
                                           f" status_code {code_from_html.status_code}", "error")
                        DataBase.update_source_code_smell(row.id, 4)
                        error_log = ErrorLog(id_source_code=row.id, ds_error=f"ERROR READING FROM GITHUB STATUS:"
                                                                             f" {code_from_html.status_code}")
                    DataBase.insert_error_log(error_log)
                    continue
                try:
                    question = self.__question + ":\n" + ' '.join(code_from_html)
                except TypeError as e:
                    question = self.__question + ":\n" + str(code_from_html)
                    LogMaker.write_log(f"Error to concat question and code (status {code.status_code}): {e} Code: {code_from_html}.Keep going...", "error")
                # if self.__limit_tokens:
                size_tokens = self.__count_tokens(question)
                if size_tokens >= self.__tokens:
                    LogMaker.write_log(f"MAXIMO DE TOKENS PARA {row.link} -> {size_tokens}.Skipping...", "warning")
                    error_log = ErrorLog(id_source_code=row.id, ds_error=f"TOKEN EXCEEDED: {size_tokens}/{self.__tokens} Tokens")
                    DataBase.insert_error_log(error_log)
                    DataBase.update_source_code_smell(row.id, 10)
                    sctq = SourceCodeToQuery(id_source_code=row.id, ds_source_code=question)
                    DataBase.insert_source_to_query(sctq)
                    continue
                LogMaker.write_log(f"length tokens  {row.link} -> {size_tokens}.", "warning")
                gpt_response = self.__gpt.gpt_response(question, row.id)
                LogMaker.write_log(f"GPT RESPONSE {gpt_response}", "info")
                if not gpt_response:
                    LogMaker.write_log(f"Fail to get GPT response for {row.link} - {row.id}", "error")
                    continue
                gpt_parser, found = self.__gpt_response_parser(gpt_response, row)
                LogMaker.write_log(f"GPT RESPONSE AFTER PARSER {gpt_parser}", "info")
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
                    url_github=row.link,
                    id_base=row.id_base,
                    nr_question=self.__question_number
                )
                try:
                    DataBase.insert_bad_smell(bad_smell)
                    DataBase.update_source_code_smell(row.id, 1)
                    LogMaker.write_log(f"Insert: [OK]", "info")
                except Exception as e:
                    LogMaker.write_log(f"ERROR to insert {bad_smell.url_github} {e}", "error")
                    error_log = ErrorLog(id_source_code=row.id,
                                         ds_error=f"ERROR TO INSERT INTO tb_bad_smell {e}")
                    DataBase.insert_error_log(error_log)
                    DataBase.update_source_code_smell(row.id, 11)
                    continue
                time.sleep(self.__request_interval)

    def start(self) -> None:
        # path: str = os.path.join(os.path.abspath(os.path.pardir), "downloaded")
        # if not os.path.exists(path):
        #    LogMaker.write_log(f"Creating {path}", "info")
        #    os.mkdir(path)
        # time.sleep(2)
        start = time.time()
        LogMaker.write_log("Running...", "info")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__code_download())
        end = time.time()
        LogMaker.write_log(f"Complete {end - start:.2f}s", "info")
