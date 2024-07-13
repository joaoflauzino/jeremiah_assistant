import functools
import unicodedata


def normalize_category(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        if "categories" in kwargs:
            categories = kwargs["categories"]

            # Normalize each category in the list
            normalized_categories = [
                "".join(c for c in unicodedata.normalize("NFD", category) if unicodedata.category(c) != "Mn").lower()
                for category in categories
            ]

            # Update the argument with the normalized categories
            kwargs["categories"] = normalized_categories

        elif "category" in kwargs:
            category = kwargs["category"]

            # Normalize category
            normalized_category = "".join(
                c for c in unicodedata.normalize("NFD", category) if unicodedata.category(c) != "Mn"
            ).lower()
            # Update the argument with the normalized category
            kwargs["category"] = normalized_category

        return func(*args, **kwargs)

    return wrapper
