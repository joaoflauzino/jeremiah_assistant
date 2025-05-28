class SpendRepositoryError(Exception):
    """Base exception class for spend repository errors."""
    ...

class SpendIntegrityRepositoryError(SpendRepositoryError):
    """Raised when Integrity error happens in repository layer."""
    ...

class TransactionRepositoryError(Exception):
    """Base exception class for transaction repository errors."""
    ...

class NotFoundError(Exception):
    """Raised when a category does not exist."""
    def __init__(self, message, user_message=None):
        super().__init__(message)
        self.user_message = user_message

class SpendServiceError(Exception):
    """Raised when an error happens in service layer"""
    def __init__(self, message, user_message=None):
        super().__init__(message)
        self.user_message = user_message

class SpendIntegrityServiceError(SpendServiceError):
    """Raised when Integrity error happens in service layer"""
    def __init__(self, message, user_message=None):
        super().__init__(message)
        self.user_message = user_message