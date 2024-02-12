import datetime
import sqlalchemy as sa
from .base import BaseModel


class PendingSourceCodeWithDuplicates(BaseModel):
    """Table responsible for the information to be searched"""

    __tablename__: str = 'vw_pending_source_code_with_duplicates'

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    id_base: int = sa.Column(sa.Integer, nullable=False)
    reviewer_id: int = sa.Column(sa.Integer, nullable=False)
    sample_id: int = sa.Column(sa.Integer, nullable=False)
    smell: str = sa.Column(sa.String(1000), nullable=False)
    severity: str = sa.Column(sa.String(1000), nullable=False)
    review_timestamp: datetime = sa.Column(sa.DateTime, default=datetime.datetime.now)
    type: str = sa.Column(sa.String(1000), nullable=False)
    code_name: str = sa.Column(sa.String(1000), nullable=False)
    repository: str = sa.Column(sa.String(1000), nullable=False)
    commit_hash: str = sa.Column(sa.String(1000), nullable=False)
    path: str = sa.Column(sa.String(1000), nullable=False)
    start_line: int = sa.Column(sa.Integer, nullable=False)
    end_line: int = sa.Column(sa.Integer, nullable=False)
    link: str = sa.Column(sa.String(1000), nullable=False)
    is_from_industry_relevant_project: int = sa.Column(sa.Integer, nullable=False)
