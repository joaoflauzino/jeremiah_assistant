class SpendRepositoryError(Exception):
    """Base exception class for spend repository errors."""
    ...

class TransactionRepositoryError(Exception):
    """Base exception class for transaction repository errors."""
    ...

class NotFoundError(Exception):
    """Raised when a category does not exist."""
    ...

class SpendServiceError(Exception):
    """Raised when an error happens in service layer"""
    ...