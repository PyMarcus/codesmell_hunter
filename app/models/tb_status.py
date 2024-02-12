import sqlalchemy as sa
from .base import BaseModel


class Status(BaseModel):
    """table that will be filled with the execution of the process."""

    __tablename__: str = 'tb_status'

    cd_status: int = sa.Column(sa.BigInteger, primary_key=True, unique=True, autoincrement=True)
    ds_status: str = sa.Column(sa.Text, nullable=True)
