import requests
import json


url = "http://localhost:8000"


class CreditCard(object):
    """
    Objetc responsible to manage credit card operations in database.
    """

    credit_card = {
        "card_id": None,
        "card_name": None,
        "closing_date": None,
        "card_limit": None,
        "record_status": None,
    }

    credit_card_name = {
        "Bradesco - JL": 1,
        "BB - JL": 2,
        "Itau - JL": 3,
        "BB - Lailla": 4,
        "Nubank - JL": 5,
        "Nubank - Lailla": 6,
    }

    board = [
        ["Bradesco - JL", "BB - JL"],
        ["Itau - JL", "BB - Lailla"],
        ["Nubank - JL", "Nubank - Lailla"],
    ]

    def __init__(self, choice) -> None:
        self.choice = choice

    def set_board(self) -> None:
        """
        Choose board that be used to complete operation.
        """
        return self.board

    def save_step_name(self, choice: str) -> None:
        """
        Save step name.
        """
        self.credit_card["action"] = choice

    def save_credit_card_name(self, name: str) -> None:
        """
        Save credit card name in global variable.
        """
        card_id = (
            max(self.credit_card_name.values()) + 1
            if name not in self.credit_card_name.keys()
            else self.credit_card_name.get(name)
        )

        record_status = 1 if self.credit_card_name.get(name) else 0

        self.credit_card["card_id"] = card_id
        self.credit_card["card_name"] = name
        self.credit_card["record_status"] = record_status

    def save_credit_card_limit(self, limit: str) -> None:
        """
        Save credit card limit in global variable.
        """
        self.credit_card["card_limit"] = float(limit)

    def save_credit_card_closing_date(self, date: str) -> None:
        """
        Save credit card limit in global variable.
        """
        self.credit_card["closing_date"] = date

    def create_credit_card_database(self) -> dict:
        """
        Return budget directly from database.
        """
        response = requests.post(
            url=f"{url}/dimension/credit_card/register",
            data=json.dumps(self.credit_card),
            timeout=500,
        )
        return response

    def clean_transaction(self) -> None:
        self.credit_card = {
            "card_id": None,
            "card_name": None,
            "closing_data": None,
            "card_limit": None,
            "record_status": None,
        }
