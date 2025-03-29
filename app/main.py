from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import schema
import crud
import models
from database import get_db,engine,SessionLocal
from sqlalchemy.orm import Session
from utils import perform_translation
from typing import List
import uuid


models.Base.metadata.create_all(bind=engine)
app=FastAPI()

templates=Jinja2Templates(directory="templates")

@app.get('/index',response_class=HTMLResponse)
def index(request:Request):
  return templates.TemplateResponse("index.html",{"request":request})

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)  

@app.post("/translate",response_model=schema.TaskResponse)
def translate(request:schema.TranslationRequest, background_tasks:BackgroundTasks,db:Session=Depends(get_db)):
  task=crud.create_translation_task(db,request.text,request.languages)
  background_tasks.add_task(perform_translation,task.id,request.text,request.languages,db)
  return schema.TaskResponse(task_id=task.id, status=task.status)

@app.get("/translate/{task_id}",response_model=schema.TranslationStatus)
def get_translate(task_id:int,db:Session=Depends(get_db)):
  task=crud.get_translation_task(db,task_id)
  if not task:
    raise HTTPException(status_code=404,detail="task not found")
  return {"task_id":task.id,"status":task.status,"translation":task.translations}
  
@app.get("/translate/content/{task_id}")
def get_translation_content(task_id:int,db:Session=Depends(get_db)):
  task=crud.get_translation_task(db,task_id)
  if not task:
    raise HTTPException(status_code=404,detail="task not found")
  return task
  