import logging
from functools import wraps

from config.exceptions import DatabaseError, SpendServiceError

import requests

logger = logging.getLogger(__name__)


def handle_request_exceptions(fields_to_return=None, re_raise=False):
    """
    Decorator para capturar exceções em funções que fazem requisições HTTP
    e retornar campos específicos em caso de erro.

    - fields_to_return: lista de nomes dos parâmetros que devem ser incluídos na resposta de erro.
    - re_raise: se True, relança a exceção após o log.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            arg_names = func.__code__.co_varnames[: func.__code__.co_argcount]
            input_data = dict(zip(arg_names, args))
            input_data.update(kwargs)

            try:
                return func(*args, **kwargs)

            except requests.exceptions.HTTPError as e:
                logger.error(
                    f"HTTP error: {e} - Response: {e.response.text if e.response else 'No response'}"
                )
                error_msg = "HTTP error"
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error: {e}")
                error_msg = "Connection error"
            except requests.exceptions.Timeout as e:
                logger.error(f"Request timed out: {e}")
                error_msg = "Request timeout"
            except requests.exceptions.RequestException as e:
                logger.error(f"General request exception: {e}")
                error_msg = "Request exception"
            except (TypeError, ValueError) as e:
                logger.error(f"Invalid input data: {e}")
                error_msg = "Invalid input data"
            except Exception as e:
                logger.exception(f"Unexpected error: {e}")
                error_msg = "Unexpected error"

            if re_raise:
                raise

            response_data = {k: input_data.get(k) for k in (fields_to_return or [])}
            response_data["error"] = error_msg
            return response_data

        return wrapper

    return decorator

def handle_service_errors(action_description: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            try:
                return fn(self, *args, **kwargs)
            except DatabaseError:
                msg = f"{action_description} | Erro de banco de dados"
                self.logger.error(msg)
                raise SpendServiceError(msg)
            except Exception:
                msg = f"{action_description} | Erro inesperado"
                self.logger.error(msg)
                raise SpendServiceError(msg)
        return wrapper
    return decorator

