import sqlalchemy as sa
from .base import BaseModel


class SourceCodeToQuery(BaseModel):
    """Table responsible for the storage the codes with errors"""

    __tablename__: str = 'tb_source_code_to_query'

    cd_query: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_source_code: int = sa.Column(sa.Integer, nullable=False)
    ds_source_code: str = sa.Column(sa.String, nullable=False)
