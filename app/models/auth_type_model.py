from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.session import Base


class AuthType(Base):
    __tablename__ = "auth_type"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    auth_data = relationship("AuthData", back_populates="auth_type_ref")
