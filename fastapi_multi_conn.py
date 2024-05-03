from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from typing import List,Annotated 
from pydantic import BaseModel,Field


app = FastAPI()

# Base class for declarative models
Base = declarative_base()

# Database connection URLs for each PostgreSQL database
DATABASE_URL_1 = "postgresql://user1:password1@localhost/db1"
DATABASE_URL_2 = "postgresql://user2:password2@localhost/db2"

# Creating SQLAlchemy engine instances
engine1 = create_engine(DATABASE_URL_1)
engine2 = create_engine(DATABASE_URL_2)

# Creating sessionmaker instances for each engine
Session1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
Session2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)
#models 

class ProvinceBase(BaseModel):
    prov_id: int 

class ProvinceSchema(ProvinceBase):
    name: str 
   
    class Config:
        orm_mode = True
        populate_by_name = True
class Province(Base):
    __tablename__ = "master_prov" 
    __table_args__ = {"schema": "p2024"}

    prov_id = Column(Integer, primary_key=True, index=True)  
    name = Column(String, index=True,)
 
    def __repr__(self):
        return f"<Province(name={self.name})>"

# Bind Province model to a specific session
Province.__table__.create(bind=engine2, checkfirst=True) 
 
def get_db1():
    db = Session1()
    try:
        yield db
    finally:
        db.close()

# Dependency to get database session for the second connection
def get_db2():
    db = Session2()
    try:
        yield db
    finally:
        db.close() 

@app.get("/models2/", response_model=List[ProvinceSchema])
def read_models2(q: Annotated[str | None, Query(min_length=3, max_length=50)] = None, skip: int = 0, limit: int = 10, db2: Session = Depends(get_db2)): 
    try: 
        data =  db2.query(Province)
        if q:
            data = data.where(Province.name.ilike(f'%{q}%'))   
        data = data.all()
    finally:
        db2.close()  
    return data 