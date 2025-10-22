from openai import OpenAI
import os
from dirs import DIRS
from typing import Optional, Dict, Any

# get openai client
def get_openai_client():
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def ask_ai(user_info: str, total_calories: float) -> str:
    """
    Send user info and total calories to OpenAI model and return a humorous, realistic training plan.
    """

    prompt = f"""
    Użytkownik(płeć, waga, wiek, wzrost): {user_info}.
    Zjadł łącznie {total_calories:.0f} kcal z McDonalda.
    Potraktuj te kalorie jako nadmiarowe.
    Napisz lekko zabawny, ale realistyczny plan treningowy,
    ile pompek, przysiadów lub kilometrów biegu musi zrobić, żeby spalić ten nadmiar.
    """

    response = get_openai_client().chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        max_tokens=500,
        messages=[
            {"role": "system", "content": "You are a fitness coach with a sense of humor."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()