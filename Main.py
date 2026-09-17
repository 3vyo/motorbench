from fastapi import FastAPI, HTTPException, Depends
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from typing import Annotated
import Models
from Database import SessionLocal
from sqlalchemy.orm import Session


app = FastAPI()


class ChoiceBase(BaseModel):
    choice_text: str = Field(min_length=1, max_length=200)
    is_correct: bool

    @field_validator('choice_text')
    @classmethod
    def choice_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('Choice text must not be empty')
        return value
class QuestionBase(BaseModel):
    question_text: str = Field(min_length=1, max_length=500)
    choices: list[ChoiceBase] = Field(min_length=2, max_length=6)

    @field_validator('question_text')
    @classmethod
    def question_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('Question text must not be empty')
        return value
    @model_validator(mode='after')
    def must_have_exactly_one_correct_choice(self):
        correct_count = sum(choice.is_correct for choice in self.choices)

        if correct_count != 1:
            raise ValueError('There must be exactly one correct choice')
        return self

class ChoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    choice_text: str
    is_correct: bool


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_text: str
    choices: list[ChoiceResponse]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



db_dependancy = Annotated[Session, Depends(get_db)]

@app.get("/")
def root():
    return {
        "message": "Quiz API is running",
        "docs": "/docs",
    }

@app.get("/questions/")
async def read_question(question_id: int, db: db_dependancy):
    result = db.query(Models.Questions).filter(Models.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code = 404, detail='Question not Found')
    return result
@app.get("/choices/{question_id}")
async def read_choices(question_id: int, db: db_dependancy):
    result = db.query(Models.Choices).filter(Models.Choices.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code = 404, detail='choice not Found')
    return result
@app.post(
    "/questions/",
    status_code=201,
    response_model=QuestionResponse,
)
def create_question(question: QuestionBase, db: db_dependancy):
    try:
        db_question = Models.Questions(
            question_text=question.question_text,
            choices=[
                Models.Choices(
                    choice_text=choice.choice_text,
                    is_correct=choice.is_correct,
                )
                for choice in question.choices
            ],
        )

        db.add(db_question)
        db.commit()
        db.refresh(db_question)

        return db_question
    except Exception:
        db.rollback()
        raise
