import requests
import json

url = "http://127.0.0.1:8000"


class Finance(object):
    """
    Objetc responsible to manage financial operations in database.
    """

    board = [
        ["Comida - Final de Semana", "Mercado"],
        ["Farmácia", "Sacolão"],
        ["Outros"],
    ]

    transaction = {
        "action": None,
        "category_id": None,
        "category_name": None,
        "budget_type": None,
        "budget": None,
    }

    d_category_name = {
        "Comida - Final de Semana": 1,
        "Mercado": 2,
        "Farmácia": 3,
        "Sacolão": 4,
        "Outros": 5,
    }

    transactions_ids = []

    def __init__(self, choice) -> None:
        self.choice = choice

    def get_transaction(self) -> dict:
        """
        Return transaction.
        """
        return self.transaction

    def get_transactions_ids(self) -> list:
        """
        Return transaction id.
        """
        return self.transactions_ids

    def get_budget_database(self, item: int) -> dict:
        """
        Return budget directly from database.
        """
        response = requests.get(
            url=f"{url}/dimension/budget", params={"items": item}, timeout=500
        )
        return response

    def get_amount_database(self, item: int) -> dict:
        """
        Return amount directly from database.
        """
        response = requests.get(
            url=f"{url}/transaction/budget", params={"items": item}, timeout=500
        )
        return response

    def set_board(self) -> None:
        """
        Choose board that be used to complete operation.
        """
        return self.board

    def save_step_name(self, choice: str) -> None:
        """
        Save step name.
        """
        self.transaction["action"] = choice

    def save_category_name(self, choice: str) -> None:
        """
        Save categoryd name.
        """
        self.transaction["category_name"] = choice
        self.transaction["category_id"] = self.d_category_name[choice]

    def set_transaction_id(self, transaction_id: list):
        self.transactions_ids.extend(transaction_id)

    def save_amount(self, choice: str) -> dict:
        """
        Save amount transaction.
        """
        self.transaction["budget"] = float(choice)
        self.transaction["budget_type"] = "Gastos"
        return self.transaction

    def save_transactions_ids(self, id) -> None:
        """
        Save transactions ids.
        """
        self.transaction["transaction_id"] = id

    def save_register(self) -> None:
        """
        Register budget transaction.
        """
        response = requests.post(
            url=f"{url}/dimension/budget/register",
            data=json.dumps(self.transaction),
            timeout=500,
        )
        return response.status_code

    def update_register(self) -> None:
        """
        Upadate budget transaction.
        """
        response = requests.put(
            url=f"{url}/dimension/budget/update",
            data=json.dumps(self.transaction),
            timeout=500,
        )
        return response.status_code

    def save_amount_register(self) -> None:
        """
        Register transaction amount.
        """
        self.transaction.pop("action")
        self.transaction.pop("category_name")
        self.transaction.pop("budget_type")
        self.transaction["amount"] = self.transaction.get("budget")

        response = requests.post(
            url=f"{url}/transaction/budget/register",
            data=json.dumps(self.transaction),
            timeout=500,
        )

        return response.status_code

    def update_amount(self) -> None:
        """
        Update amount transaction.
        """

        self.transaction.pop("action")
        self.transaction.pop("category_name")
        self.transaction.pop("budget_type")
        self.transaction["amount"] = self.transaction.get("budget")

        response = requests.put(
            url=f"{url}/transaction/budget/update",
            data=json.dumps(self.transaction),
            timeout=500,
        )
        return response.status_code

    def delete_amount(self) -> None:
        """
        Delete amount transaction.
        """
        response = requests.delete(
            url=f"{url}/transaction/budget/delete",
            data=json.dumps(self.transaction),
            timeout=500,
        )
        return response.status_code

    def clean_transaction(self) -> None:
        self.transaction = {
            "action": None,
            "category_id": None,
            "category_name": None,
            "budget_type": None,
            "budget": None,
        }
