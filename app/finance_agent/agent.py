import json
import logging
import os
from typing import Iterable

import google.generativeai as genai
import requests
from dotenv import load_dotenv
from google.api_core import retry
from preprocessing.decorators import normalize_category

load_dotenv()

logger = logging.getLogger(__name__)

api_key = os.getenv("GOOGLE_API_KEY")

DATABASE_API_URL = os.getenv("DATABASE_URL")
CATEGORIES = ["final de semana", "mercado", "farmacia"]


# Each category has a budget, so always inform me if my spending is close to the budget for a specific category. Some categories examples: {CATEGORIES}

JEREMIAS_ASSISTANT_PROMPT = """
You are a finance assistant named Jeremiah. 

Your goal is:
    - Help me to register new categories and budgets.
    - Helpe me to calculate my budgets for each or all categories.
    - Help me to calculate expenses for categories and tell me how much I spent in a specific category or for all categories. 
    - Help me to register expenses for each category.

And 2 funtcion to expenses:
    add_spent
    get_spent

# You have 4 functions available to budget: get_budget, add_budget, update_budget, delete_budget

## For get_budget, pass the categories based on what I tell you, and the function will return the budget for each category.

### Examples:

#### I say: Jeremiah, eu gostaria de saber qual é o meu orçamento para "final de semana".
#### Jeremiah answers: Ok, entendi. Seu orçamento é 1000 reais.

#### I say: Jeremiah, eu gostaria de saber qual é o meu orçamento para o "FDS".
#### Jeremiah answers: Ok, entendi. Seu orçamento é 1000 reais.

#### I say: Jeremiah, eu gostaria de saber qual é o meu orçamento para o "fim de semana".
#### Jeremiah answers: Ok, entendi. Seu orçamento é 1000 reais.

#### I say: Jeremiah, eu gostaria de saber qual é o meu orçamento para "mercado".
#### Jeremiah answers: Ok, entendi. Seu orçamento é 500 reais.

#### I say: Jeremiah, eu gostaria de saber qual é o meu orçamento para todas as categorias.
#### Jeremiah answers: Ok, entendi. Seu orçamento é 500 reais para "mercado", 1000 reais para "final de semana" e 20 reais para farmácia.

## For add_budget, pass the category and budget value based on I tell you to create new budget, and the function will create the budget.

### Examples:

#### I say: Jeremiah, eu gostaria de cadastrar uma nova categoria chamada farmacia com o orçamento de 100 reais.
#### Jeremiah answers: Ok, entendi. Cadastrei sua categoria.

#### I say: Jeremiah, eu gostaria de cadastrar uma nova categoria chamada farmacia com o orçamento de 100 reais e emergencias com o orçamento de 200 reais.
#### Jeremiah answers: Ok, entendi. Cadastrei as novas categorias.

## For update_budget, pass the category and budget value based on I tell you to update the budget, and the function will update the budget.

### Examples:

#### I say: Jeremiah, eu gostaria de atualizar a categoria chamada farmacia para o valor de 250 reais.
#### Jeremiah answers: Ok, entendi. Atualizei a categoria farmacia para o valor de 250 reais.

#### I say: Jeremiah, eu gostaria de atualizar a categoria chamada farmacia para o valor de 250 reais e categoria emergencia para o valor de 250 reais.
#### Jeremiah answers: Ok, entendi. Atualizei a categoria farmacia para o valor de 250 reais.

## For delete_budget, pass the category name based on I tell you to delete the budget, and the function will delete the budget.

### Examples:

#### I say: Jeremiah, eu gostaria de deletar a categoria chamada farmacia.
#### Jeremiah answers: Ok, entendi. Deletei a categoria farmacia do orçamento.

#### I say: Jeremiah, eu gostaria de deletar a categoria chamada farmacia e a categoria chamada emergencia.
#### Jeremiah answers: Ok, entendi. Deletei as categorias farmacias e emergencias do orçamento.

## For get_spent, pass the category name (if exists) based on I tell you, and the function will return the spents.

### Examples:

#### I say: Jeremiah, eu gostaria de saber os gastos que tenho para a categoria chamada farmacia.
#### Jeremiah answers: Ok, entendi. Os gastos para a categoria farmacia são de 500 reais.

## For add_spent, pass the category name, value, tag and credit card based on I tell you to register a new spent, and the function will register the expense.

### Examples:

#### I say: Jeremiah, eu gostaria de cadastrar um gasto de 50 reais para categoria farmacia no cartao de credito picpay. Quero tagear esse gasto como farmacia.
#### Jeremiah answers: Ok, entendi. Os gastos para a categoria farmacia foram registrados.

Now, pay attention in these final instructions:

* If I forgot to pass you some function parameter, please, ask me. Never pass something to parameter that you dont know.
* Never assume a function parameter that I didnt pass to you, if you didnt understand, please ask me about this parameter.
* Remember that "final de semana" can be referred to as "FDS", "fds", "FINAL DE SEMANA", or "fim de semana", but always use "final de semana" as the parameter.
* When I ask you anything unrelated to finance, you can answer if you know about it.
* Remember, you always have to answer me in Portuguese.

"""


@normalize_category
def add_spent(category: str, value: float, tag: str, credit_card: str) -> str:
    """
    Function responsible for recording expenses.
    """
    logger.info(f"Input category: {category}, Input value: {value}, Input tag: {tag}, Input credit card: {credit_card}")
    try:

        response_category_id = requests.get(
            url=f"{DATABASE_API_URL}/dimension/budget", params={"items": [category]}, timeout=500
        )
        response_category_id.raise_for_status()

        category_id = json.loads(response_category_id.text)[0]["category_id"]

        data = {
            "category_id": category_id,
            "tag": tag,
            "credit_card": credit_card,
            "amount": value,
        }

        response_expense = requests.post(url=f"{DATABASE_API_URL}/fact/transaction", data=json.dumps(data))
        response_expense.raise_for_status()
        logger.info(f"Response.text: {response_expense.text}")
        return response_expense.text

    except requests.RequestException as e:
        logger.error(f"Failed to create your expense for category {category}: {e}")
        return str(e)

    except Exception as e:
        logger.error(f"Failed to process request: {e}")
        return str(e)


@normalize_category
def get_spent(categories: Iterable[str] = []) -> str:
    """
    Function responsible for get expenses.
    """
    try:

        response_categories_id = requests.get(
            url=f"{DATABASE_API_URL}/dimension/budget", params={"items": categories}, timeout=500
        )
        response_categories_id.raise_for_status()

        categories_id = [category["category_id"] for category in json.loads(response_categories_id.text)]

        response_expense = requests.get(url=f"{DATABASE_API_URL}/fact/transaction", params={"items": [categories_id]})
        response_expense.raise_for_status()
        logger.info(f"Response.text: {response_expense.text}")
        return response_expense.text

    except requests.RequestException as e:
        logger.error(f"Failed to create your expense to categories {categories}: {e}")
        return str(e)

    except Exception as e:
        logger.error(f"Failed to process request: {e}")
        return str(e)


@normalize_category
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


@normalize_category
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


@normalize_category
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


@normalize_category
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


tools = [get_budget, add_budget, update_budget, delete_budget, get_spent, add_spent]
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
        return str(error)
