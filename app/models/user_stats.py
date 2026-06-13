from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import func

from app.db.database import Base

class UserStats(Base):
    __tablename__ = "user_stats"
    id=Column(Integer,primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    xp=Column(Integer,nullable=False, default=0)
    level=Column(Integer,nullable=False, default=1)
    day_streak=Column(Integer,nullable=False,default=0)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )