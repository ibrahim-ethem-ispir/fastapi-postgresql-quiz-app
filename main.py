from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool

class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/questions/{question_id}")
async def read_question(question_id: int, db: db_dependency):
    db_question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question

@app.get("/choices/{question_id}")
async def read_choice(question_id: int, db: db_dependency):
    db_choice = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    if db_choice is None:
        raise HTTPException(status_code=404, detail="Choice not found")
    return db_choice

@app.post("/questions")
async def create_question(question: QuestionBase, db: db_dependency):
    db_question = models.Question(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice = models.Choices(choice_text=choice.choice_text, is_correct=choice.is_correct, question_id=db_question.id)
        db.add(db_choice)
    
    db.commit()
    return db_question
