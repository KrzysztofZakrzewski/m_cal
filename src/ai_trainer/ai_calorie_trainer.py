from openai import OpenAI
import os
from src.dirs import DIRS
from typing import Optional, Dict, Any

# get openai client
def get_openai_client():
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def ask_ai(user_info: str, total_calories: float, filtered_period_time: str) -> str:
    """
    Send user info and total calories to OpenAI model and return a humorous, realistic training plan.
    """

    prompt = f"""
    Użytkownik(płeć, wiek, waga, wzrost): {user_info}.
    Zjadł łącznie {total_calories:.0f} kcal z McDonalda,
    okresie czasu {filtered_period_time}.
    Potraktuj te kalorie jako nadmiarowe.
    Napisz realistyczny plan treningowy,
    ile pompek, przysiadów lub kilometrów biegu musi zrobić użytkownik, żeby spalić ten nadmiar.
    Powiec jaki okres czasu został Ci przekazany, w którym użytkownik wchłaniał kalorie.
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