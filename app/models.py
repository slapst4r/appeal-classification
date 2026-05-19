from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Appeal(Base):
    __tablename__ = 'appeals'
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    contains_explicit = Column(Boolean, default=False)
    unclassified_reason = Column(String, nullable=True)
    category = relationship("AppealCategory", back_populates="appeal", uselist=False)


class AppealCategory(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    appeal_id = Column(Integer, ForeignKey('appeals.id'))
    category = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    appeal = relationship("Appeal", back_populates="category")