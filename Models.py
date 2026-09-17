from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from Database import Base
from sqlalchemy.orm import relationship

class Questions(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key = True, index = True)
    question_text = Column(String(500), nullable=False)

    choices = relationship("Choices", back_populates="question", cascade="all, delete-orphan", passive_deletes=True)
class Choices(Base):
    __tablename__ = 'choices'
    id = Column(Integer, primary_key = True)
    choice_text = Column(String(200), nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)

    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)

    question = relationship("Questions", back_populates="choices")

    