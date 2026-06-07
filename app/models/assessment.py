from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func

from app.db.database import Base

class Assessment(Base):
    __tablename__="assessments"
    id=Column(Integer, primary_key=True,index=True)
    user_id=Column(
        Integer,
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    social_situation=Column(String,nullable=False)
    current_goal=Column(String,nullable=False)
    self_improvement_consistency=Column(
        String,
        nullable=False
    )
    biggest_obstacle=Column(String,nullable=False)
    created_at=Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at=Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )