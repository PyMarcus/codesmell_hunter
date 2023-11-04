import sqlalchemy as sa

from .base import BaseModel


class BadSmell(BaseModel):
    __tablename__: str = 'tb_bad_smell'

    id_bad_smell: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_source_code: int = sa.Column(sa.Integer, nullable=True)
    index: int = sa.Column(sa.Integer, nullable=True)
    index_base: int = sa.Column(sa.Integer, nullable=True)
    chat_gpt_response: str = sa.Column(sa.Text, nullable=True)
    question: str = sa.Column(sa.Text, nullable=True)
    badsmell_base: str = sa.Column(sa.Text, nullable=True)
    bad_smell_gpt: str = sa.Column(sa.Text, nullable=True)
    found_any: bool = sa.Column(sa.Boolean, default=True)
    valid_bad_smell: bool = sa.Column(sa.Boolean)
    bad_smell_in_base: bool = sa.Column(sa.Boolean, default=True)
    bad_smell_not_in_the_base: str = sa.Column(sa.Text, nullable=True)
    bad_smell_not_found: int = sa.Column(sa.Text, nullable=True)
    url_github: str = sa.Column(sa.String(300), nullable=False)
