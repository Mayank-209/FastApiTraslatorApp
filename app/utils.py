from sqlalchemy.orm import Session
from crud import update_translation_task
from dotenv import load_dotenv
import json
import requests
import re
import os

# Load API key from environment variables
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

def perform_translation(task_id: int, text: str, languages: list, db: Session):
    translation = {}

    for lang in languages:
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": "deepseek/deepseek-r1-zero:free",
                    "messages": [
                        {"role": "system", "content": f"You are a helpful assistant that translates text into {lang}"},
                        {"role": "user", "content": text}
                    ],
                })
            )
            
            response_json = response.json()
            choices = response_json.get("choices", [])

            if choices and isinstance(choices, list):
                translated_text = choices[0].get("message", {}).get("content", "").strip()
            else:
                translated_text = "Translation failed"

            # Remove \boxed{} if present
            translated_text = re.sub(r'\\boxed{(.+?)}', r'\1', translated_text)

            print(f"Translation for {lang}: {translated_text}")
            translation[lang] = translated_text

        except Exception as e:
            print(f"Error translating in {lang}: {e}")
            translation[lang] = f"Error: {e}"

    # Update the translation task in the database
    update_translation_task(db, task_id, translation)

