import json
import os
from typing import Iterable, List

import requests
from config.logs import setup_logger
from config.request_exceptions import handle_request_exceptions

logger = setup_logger(__name__)

DATABASE_API_URL = os.getenv("DATABASE_URL")

@handle_request_exceptions(fields_to_return=["category", "value", "tag", "credit_card"])
def add_spent(category: str, value: float, tag: str, credit_card: str) -> str:
    """
    Function responsible for recording spents.
    """
    logger.info(
        f"Input category: {category}, Input value: {value}, Input tag: {tag}, Input credit card: {credit_card}"
    )

    # É responsabilidade do serviço validar se aquele ID informado pertence a uma
    # categoria ja existente... e não do agente. Corrigir isso.

    response_category_id = requests.get(
        url=f"{DATABASE_API_URL}/dimension/budget",
        params={"items": [category]},
        timeout=500,
    )

    category_id = json.loads(response_category_id.text)[0]["category_id"]

    response = requests.post(
        url=f"{DATABASE_API_URL}/transaction/budget",
        data=json.dumps(
            {
                "category_id": category_id,
                "tag": tag,
                "credit_card": credit_card,
                "amount": value
            }
        ),
    )
    response.raise_for_status()
    logger.info(f"Response.text: {response.text}")
    return response.text


@handle_request_exceptions(fields_to_return=["categories"])
def get_spent(categories: List[str] = []) -> list | str:
    """
    Function responsible for get spents.
    """
    response = requests.get(
        url=f"{DATABASE_API_URL}/transaction/budget", params={"items": categories}
    )
    response.raise_for_status()
    logger.info(f"Response.text: {response.text}")
    return response.text


@handle_request_exceptions(fields_to_return=["category", "value"])
def add_budget(category: str, value: float) -> str:
    """
    Function responsible to create budget for category or create a new one.
    """
    logger.info(f"Input category: {category}, Input values: {value}")
    response = requests.post(
        url=f"{DATABASE_API_URL}/dimension/budget",
        data=json.dumps({"category_name": category, "budget": value}),
    )
    response.raise_for_status()
    logger.info(f"Response.text: {response.text}")
    return response.text


@handle_request_exceptions(fields_to_return=["category", "value"])
def update_budget(category: str, value: float) -> str:
    """
    Function responsible to update budget for category.
    """
    logger.info(f"Input category: {category}, Input values: {value}")
    response = requests.put(
        url=f"{DATABASE_API_URL}/dimension/budget",
        data=json.dumps({"category_name": category, "budget": value}),
        timeout=500,
    )
    response.raise_for_status()
    logger.info(f"Response.text: {response.text}")
    return response.text


@handle_request_exceptions(fields_to_return=["categories"])
def get_budget(categories: Iterable[str] = []) -> list | str:
    """
    Function responsible to get budget value for each or all categories.
    """
    logger.info(f"Input categories: {categories}")
    response = requests.get(
        url=f"{DATABASE_API_URL}/dimension/budget",
        params={"items": categories},
        timeout=500,
    )
    response.raise_for_status()
    logger.info(f"Response.text: {response.text}")
    return response.text


@handle_request_exceptions(fields_to_return=["category"])
def delete_budget(category: str) -> str:
    """
    Function responsible to delete budget value for specific category.
    """
    logger.info(f"Input category: {category}")
    response = requests.delete(
        url=f"{DATABASE_API_URL}/dimension/budget",
        data=json.dumps({"category_name": category}),
    )
    response.raise_for_status()
    logger.info(f"Response.text: {response.text}")
    return response.text
