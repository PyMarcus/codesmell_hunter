import typing

import sqlalchemy as sa
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from .constants import DATABASE
from .constants import HOST
from .constants import NAME
from .constants import PASSWORD
from .constants import PORT
from app.package.register import LogMaker


__engine: typing.Optional[Engine] = None


def create_engine() -> Engine | None:
    global __engine

    if __engine:
        return
    print(NAME)
    if not NAME or not HOST or not PASSWORD or not PORT or not DATABASE:
        LogMaker.write_log(".env is not set", "error")
        raise ".env is not set"
    conn_str: str = f"postgresql://{NAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    __engine = sa.create_engine(url=conn_str, echo=False)
    return __engine


def create_session() -> Session:
    global __engine

    if not __engine:
        create_engine()
    return sessionmaker(__engine, expire_on_commit=False, class_=Session)()
