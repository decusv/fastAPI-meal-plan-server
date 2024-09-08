from typing import List
import random
import string
import requests
from requests_toolbelt.utils import dump
from config import API_KEY

def generate_identifier() -> str:
    """
    Generate a 7-character alphanumeric identifier.

    Returns:
        str: The generated identifier.
    """
    characters = string.ascii_uppercase  + string.digits
    return ''.join(random.choice(characters) for _ in range(7))


def generate_meal_plan(meal_tags: List[str]) -> dict:
    """
    Generate a meal plan using the ChatGPT API.

    Args:
        meal_tags (List[str]): List of meal tags to be used as part of generating the query.

    Returns:
        dict: A dictionary containing the generated meal plan.
    
    """
    chatgpt_endpoint = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    with open("prompt.txt", "r", encoding="utf-8") as file:
        prompt = file.read()

    prefix = "The following are meal tags that will be used as part of generating the query:  "
    tags_string = ','.join(meal_tags)
    tags_string_with_prefix = prefix + tags_string # Convert list to a comma separated string.

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": tags_string_with_prefix},  # Using the passed meal tags
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        chatgpt_endpoint,
        headers=headers,
        json=payload,
        timeout=30  # Add a timeout value in seconds
    )

    data = dump.dump_all(response)
    print(data.decode('utf-8'))

    data = response.json()
    generated_meal_plan = data.get("choices", [])[0].get("message", {}).get("content", "")

    return {"generated_meal_plan": generated_meal_plan}