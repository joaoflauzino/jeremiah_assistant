import requests
import json

url = "http://127.0.0.1:8000"


class Finance(object):
    """
    Objetc responsible to manage financial operations in database.
    """

    global board

    board = {
        "cadastrar limite de gastos": [
            ["Comida - Final de Semana", "Mercado"],
            ["Farmácia", "Sacolão"],
            ["Outros"],
        ],
        "consultar limite de gastos": [
            ["Comida - Final de Semana", "Mercado"],
            ["Farmácia", "Sacolão"],
            ["Outros"],
        ],
    }

    global budget

    budget = {
        "action": None,
        "category_id": None,
        "category_name": None,
        "budget_type": None,
        "budget": None,
    }

    global d_category_name

    d_category_name = {
        "Comida - Final de Semana": 1,
        "Mercado": 2,
        "Farmácia": 3,
        "Sacolão": 4,
        "Outros": 5,
    }

    def __init__(self, choice) -> None:
        self.choice = choice

    def get_budget(self) -> dict:
        """
        Return budget.
        """
        return budget

    def get_budget_database(self, item: int) -> dict:
        """
        Return budget directly from database.
        """
        response = requests.get(
            url=f"{url}/dimension/budget", params={"items": item}, timeout=500
        )
        return response

    def set_board(self) -> None:
        """
        Choose board that be used to complete operation.
        """
        return board[self.choice]

    def save_step_name(self, choice: str) -> None:
        """
        Save step name.
        """
        budget["action"] = choice

    def save_category_name(self, choice: str) -> None:
        """
        Save categoryd name.
        """
        budget["category_name"] = choice
        budget["category_id"] = d_category_name[choice]

    def save_amount(self, choice: str) -> dict:
        """
        Save amount transaction.
        """
        budget["budget"] = float(choice)
        budget["budget_type"] = "Gastos"
        return budget

    def save_register(self) -> None:
        """
        Register transaction.
        """
        response = requests.post(
            url=f"{url}/dimension/budget/register", data=json.dumps(budget), timeout=500
        )
        return response.status_code
