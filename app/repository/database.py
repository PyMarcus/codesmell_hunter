import typing

from app.config import create_session
from app.models import BadSmell
from app.models import SourceCodeSmell


class DataBase:
    @staticmethod
    def select_all_source_code_smell() -> typing.List[typing.Type[SourceCodeSmell]] | None:
        with create_session() as session:
            source_code: typing.List[typing.Type[SourceCodeSmell]] | None = session.query(SourceCodeSmell).all()
            if source_code:
                return source_code
            return None

    @staticmethod
    def select_all_bad_smell() -> typing.List[typing.Type[BadSmell]] | None:
        with create_session() as session:
            bad_smells: typing.List[typing.Type[BadSmell]] | None = session.query(BadSmell).all()
            if bad_smells:
                return bad_smells
            return None

    @staticmethod
    def insert_bad_smell(bad_smell: BadSmell) -> bool:
        with create_session() as session:
            if bad_smell:
                session.add(bad_smell)
                session.commit()
                return True
            return False
