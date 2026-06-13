from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import func

from app.db.database import Base
class PersonaReport(Base):
    __tablename__ = "persona_reports"
    id = Column(Integer, primary_key=True, index=True)
    user_id=Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    report_data=Column(
        Text,
        nullable=False,
    )
    created_at=Column(
        DateTime(timezone=True),
        server_default=func.now()
    )