import json
import logging
import os
from typing import Iterable

import google.generativeai as genai
import requests
from dotenv import load_dotenv
from google.api_core import retry

load_dotenv()


logger = logging.getLogger(__name__)


DATABASE_API_URL = os.getenv("DATABASE_URL")

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise EnvironmentError("GOOGLE_API_KEY environment variable not set.")
genai.configure(api_key=api_key)

CATEGORIES = ["final de semana", "mercado", "farmacia"]

JEREMIAS_ASSISTANT_PROMPT = f"""
You are a finance assistant named Jeremiah. 

Your goal is:
    - Help me to register new categories and budgets.
    - Helpe me to calculate my budgets for each or all categories.
    - Help me to calculate expenses for categories and tell me how much I spent in a specific category or for all categories. 
    - Help me to register expenses for each category.

Each category has a budget, so always inform me if my spending is close to the budget for a specific category. Some categories examples: {CATEGORIES}

Remember that "final de semana" can be referred to as "FDS", "fds", "FINAL DE SEMANA", or "fim de semana", but always use "final de semana" as the parameter.

You have 3 functions available: get_budget, add_budget and update_budget

For get_budget, pass the categories on what I tell you, and the function will return the budget for each category.
For add_budget, pass the category and budget value base on I tell you to create new budget, and the function will create the budget.
For update_budget, pass the category and budget value base on I tell you to update the budget, and the function will update the budget.
For delete_budget, pass the category name base on I tell you to delete the budget, and the function will delete the budget.

Examples:

I say: Jeremiah, eu gostaria de saber qual é o meu orçamento para "final de semana".
Jeremiah answers: Ok, entendi. Seu orçamento é 1000 reais.

I say: Jeremiah, eu gostaria de saber qual é o meu orçamento para o "FDS".
Jeremiah answers: Ok, entendi. Seu orçamento é 1000 reais.

I say: Jeremiah, eu gostaria de saber qual é o meu orçamento para o "fim de semana".
Jeremiah answers: Ok, entendi. Seu orçamento é 1000 reais.

I say: Jeremiah, eu gostaria de saber qual é o meu orçamento para "mercado".
Jeremiah answers: Ok, entendi. Seu orçamento é 500 reais.

I say: Jeremiah, eu gostaria de saber qual é o meu orçamento para todas as categorias.
Jeremiah answers: Ok, entendi. Seu orçamento é 500 reais para "mercado", 1000 reais para "final de semana" e 20 reais para farmácia.

I say: Jeremiah, eu gostaria de cadastrar uma nova categoria chamada farmacia com o orçamento de 100 reais.
Jeremiah answers: Ok, entendi. Cadastrei sua categoria.

When I ask you anything unrelated to finance, you can answer if you know about it.

Remember, you always have to answer me in Portuguese.
"""


def add_budget(category: str, value: float) -> str:
    """
    Function responsible to create budget for category.
    """
    try:
        logger.info(f"Input category: {category}, Input values: {value}")
        response = requests.post(
            url=f"{DATABASE_API_URL}/dimension/budget",
            data=json.dumps({"category_name": category, "budget": value}),
        )
        response.raise_for_status()
        logger.info(f"Response.text: {response.text}")
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to create budget for categories {category}: {e}")
        return str(e)


def update_budget(category: str, value: float) -> str:
    """
    Function responsible to update budget for category.
    """
    try:
        logger.info(f"Input category: {category}, Input values: {value}")
        response = requests.put(
            url=f"{DATABASE_API_URL}/dimension/budget",
            data=json.dumps({"category_name": category, "budget": value}),
            timeout=500,
        )
        response.raise_for_status()
        logger.info(f"Response.text: {response.text}")
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to update budget for categories {category}: {e}")
        return str(e)


def get_budget(categories: Iterable[str] = []) -> str:
    """
    Function responsible to get budget value for each or all categories.
    """
    try:
        logger.info(f"Input categories: {categories}")
        response = requests.get(url=f"{DATABASE_API_URL}/dimension/budget", params={"items": categories}, timeout=500)
        response.raise_for_status()
        logger.info(f"Response.text: {response.text}")
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to get budget for categories {categories}: {e}")
        return str(e)


def delete_budget(category: str) -> str:
    """
    Function responsible to delete budget value for specific category.
    """
    try:
        logger.info(f"Input category: {category}")
        response = requests.delete(
            url=f"{DATABASE_API_URL}/dimension/budget",
            data=json.dumps({"category_name": category}),
        )
        response.raise_for_status()
        logger.info(f"Response.text: {response.text}")
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to delete category {category}: {e}")
        return str(e)


tools = [get_budget, add_budget, update_budget, delete_budget]
model_name = "gemini-1.0-pro-latest"
model = genai.GenerativeModel(model_name, tools=tools)

convo = model.start_chat(
    history=[
        {"role": "user", "parts": [JEREMIAS_ASSISTANT_PROMPT]},
        {"role": "model", "parts": ["OK I understand. I will do my best!"]},
    ],
    enable_automatic_function_calling=True,
)


@retry.Retry(initial=30)
def send_message(message: str) -> str:
    try:
        response = convo.send_message(message)
        return response.text
    except Exception as error:
        logger.error(f"Failed to send message: {error}")
        return error
