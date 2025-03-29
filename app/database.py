import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()

def get_db():
  db=SessionLocal()
  try:
    yield db
  finally:
    db.close()  

SQLALCCHEMY_DATABASE_URL=os.getenv("DATABASE_URL")
OPENI_API_KEY=os.getenv("OPENAI_API_KEY")



engine=create_engine(SQLALCCHEMY_DATABASE_URL)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)