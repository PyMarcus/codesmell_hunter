import sqlalchemy as sa
from .base import BaseModel


class ErrorLog(BaseModel):
    """Table responsible for the storage the error logs"""

    __tablename__: str = 'tb_error_log'

    cd_error_log: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_source_code: int = sa.Column(sa.Integer, nullable=False)
    ds_error: str = sa.Column(sa.Text, nullable=False)
