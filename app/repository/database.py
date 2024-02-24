import typing

from app.config import create_session
from app.models import BadSmell
from app.models import SourceCodeSmell
from app.models import PendingSourceCodeWithDuplicates
from app.models import ErrorLog
from app.models import SourceCodeToQuery


class DataBase:
    @staticmethod
    def select_all_source_code_smell() -> typing.List[typing.Type[SourceCodeSmell]] | None:
        with create_session() as session:
            source_code: typing.List[typing.Type[SourceCodeSmell]] | None = session.query(SourceCodeSmell).all()
            if source_code:
                return source_code
            return None

    @staticmethod
    def select_all_pending_source_code_with_duplicates(offset: int) -> (
            typing.List[typing.Type[SourceCodeSmell]] | None):
        with (create_session() as session):
            source_code: typing.List[typing.Type[SourceCodeSmell]] | None = session.query(
                SourceCodeSmell).filter(SourceCodeSmell.id.in_((5499, 5714))).all()
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

    @staticmethod
    def insert_error_log(error_log: ErrorLog) -> bool:
        with create_session() as session:
            if error_log:
                session.add(error_log)
                session.commit()
                return True
            return False

    @staticmethod
    def insert_source_to_query(source: SourceCodeToQuery) -> bool:
        with create_session() as session:
            if source:
                session.add(source)
                session.commit()
                return True
            return False

    @staticmethod
    def update_source_code_smell(scs_id: int, cd_status: int) -> bool:
        with create_session() as session:
            sc = session.query(SourceCodeSmell).filter_by(id=scs_id).first()
            if sc:
                sc.cd_status = cd_status
                session.commit()
                return True
            return False
