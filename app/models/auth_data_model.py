from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class ProviderType(enum.Enum):
    GOOGLE = "google"
    APPLE = "apple"
    FACEBOOK = "facebook"
    EMAIL = "email"
    PHONE = "phone"


class AuthData(Base):
    __tablename__ = "auth_data"

    id = Column(Integer, primary_key=True, index=True)
    auth_account_id = Column(Integer, ForeignKey("auth.id", ondelete="CASCADE"), nullable=False)
    auth_type_id = Column(Integer, ForeignKey("auth_type.id", ondelete="CASCADE"), nullable=False)
    provider_type = Column(Enum(ProviderType), nullable=False)
    auth_identifier = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    auth = relationship("Auth", back_populates="auth_data")
    auth_type_ref = relationship("AuthType", back_populates="auth_data")

    __table_args__ = (
        UniqueConstraint("auth_identifier", "provider_type", name="uq_auth_identifier_provider"),
    )
