from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class SessionAction(enum.Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"


class SessionAudit(Base):
    __tablename__ = "session_audit"

    id = Column(Integer, primary_key=True, index=True)
    auth_id = Column(Integer, ForeignKey("auth.id", ondelete="CASCADE"), nullable=False)
    action = Column(Enum(SessionAction), nullable=False)
    ip_address = Column(String(64))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    auth = relationship("Auth", back_populates="sessions")
