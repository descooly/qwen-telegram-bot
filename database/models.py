# database/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database.session import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(100), nullable=True)

    fio = Column(String(500), nullable=False)
    phone = Column(String(200), nullable=False)
    comment = Column(Text, nullable=True)

    status = Column(String(50), default="new")  # new, processed, cancelled
    timestamp = Column(DateTime, server_default=func.now())