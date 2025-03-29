import openai
from sqlalchemy.orm import Session
from crud import update_translation_task
from dotenv import load_dotenv
import json
import requests
import re


import os
OPENAI=os.getenv("OPENAI_API_KEY")

openai.api_key=OPENAI

def perform_translation(task_id:int,text:str,languages:list,db:Session):
  translation={}
  for lang in languages:
    try:
      # response=openai.ChatCompletion.create(
      #   model="gpt-4",
      #   messages=[
      #     {"role":"system","content":f"You are a helpful assistant that translates text into {lang}"},
      #     {"role":"user","content":text}
      #   ],
      #   max_tokens=1000
      # )
      response = requests.post(
      url="https://openrouter.ai/api/v1/chat/completions",
      headers={
         "Authorization": "Bearer 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",
         "Content-Type": "application/json",
         "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
         "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
              },
      data=json.dumps({
         "model": "deepseek/deepseek-r1-zero:free",
         "messages":[
          {"role":"system","content":f"You are a helpful assistant that translates text into {lang}"},
          {"role":"user","content":text}
         ],
    
       })
      )
      response_json = response.json()
      translated_text = response_json.get('choices', [{}])[0].get('message', {}).get('content', "").strip()

      # Remove \boxed{} if present
      translated_text = re.sub(r'\\boxed{(.+?)}', r'\1', translated_text)
      print(translated_text)
      translation[lang] = translated_text if translated_text else "Translation failed"
      print(translation)

    except Exception as e:
      print(f"Error translating in language {lang}:{e}")
      translation[lang]=f"Error: {e}"  
    except Exception as e:
      print(f"Unexpected error:{e}")  
  update_translation_task(db,task_id,translation)
