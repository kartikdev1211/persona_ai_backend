from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func

from app.db.database import Base
class PersonaProfile(Base):
    __tablename__="persona_profiles"
    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    persona_name = Column(String(30), nullable=False)

    avatar_index = Column(
        Integer,
        nullable=False,
    )

    confidence_level = Column(
        String,
        nullable=False,
    )

    focus_goal = Column(
        String,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )