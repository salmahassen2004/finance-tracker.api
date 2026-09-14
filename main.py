from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from database import SessionLocal, engine
from models import Base, Transaction as TransactionModel

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency: get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request schema
class Transaction(BaseModel):
    amount: float
    category: str

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Finance Tracker API with PostgreSQL is running!"}

# Create transaction
@app.post("/transactions")
def add_transaction(transaction: Transaction, db: Session = Depends(get_db)):
    new_transaction = TransactionModel(
        amount=transaction.amount,
        category=transaction.category
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction

# Get transactions (with optional filtering)
@app.get("/transactions")
def get_transactions(category: str = None, db: Session = Depends(get_db)):
    if category:
        return db.query(TransactionModel).filter(
            TransactionModel.category == category
        ).all()
    return db.query(TransactionModel).all()

# Get total spending
@app.get("/transactions/total")
def get_total(db: Session = Depends(get_db)):
    total = db.query(func.sum(TransactionModel.amount)).scalar()
    return {"total": total or 0}