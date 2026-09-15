from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import SessionLocal, engine
from models import Base, User, Transaction as TransactionModel

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class UserCreate(BaseModel):
    email: str
    password: str

class Transaction(BaseModel):
    amount: float
    category: str

# Signup

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)

    new_user = User(
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created"}

# Login
@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ✅ correct order
    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"id": new_user.id, "email": new_user.email}

# Add transaction (no auth yet — next step)
@app.post("/transactions")
def add_transaction(transaction: Transaction, db: Session = Depends(get_db)):
    new_transaction = TransactionModel(
        amount=transaction.amount,
        category=transaction.category,
        user_id=1  # temporary
    )
    db.add(new_transaction)
    db.commit()
    return new_transaction

@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(TransactionModel).all()