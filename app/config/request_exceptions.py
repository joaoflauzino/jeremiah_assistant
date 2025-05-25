import logging
from functools import wraps

from config.exceptions import SpendRepositoryError, SpendServiceError, NotFoundError
import requests

logger = logging.getLogger(__name__)

def handle_request_exceptions(fields_to_return=None, re_raise=False):
    """
    Decorator to handle exceptions in functions that perform HTTP requests.

    Logs different types of `requests` exceptions (e.g., HTTPError, Timeout, etc.)
    and optionally returns a dictionary with selected input fields and an error message.

    Args:
        fields_to_return (list[str], optional): List of input parameter names to include in the error response.
        re_raise (bool, optional): If True, re-raises the exception after logging it. Defaults to False.

    Returns:
        function: Wrapped function with exception handling.
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
    """
    Decorator to handle exceptions in service layer methods.

    Captures exceptions related to repository calls or general service errors,
    logs a custom action description, and raises a standardized `SpendServiceError`.

    Args:
        action_description (str): A message describing the action being attempted. Used in logs and errors.

    Returns:
        function: Wrapped function with error handling and logging.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            try:
                return fn(self, *args, **kwargs)
            except SpendRepositoryError:
                self.logger.error(action_description)
                raise SpendServiceError(action_description)
            except NotFoundError:
                raise NotFoundError(action_description)
            except Exception:
                self.logger.error(action_description)
                raise SpendServiceError(action_description)
        return wrapper
    return decorator
