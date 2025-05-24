class RepositoryError(Exception):
    """Base exception class for repository errors."""
    ...


class DatabaseError(RepositoryError):
    """Raised when a database operation fails."""
    ...

class NotFoundError(Exception):
    """Raised when a category does not exist."""
    ...

class SpendServiceError(Exception):
    """Raised when an error happens in service layer"""
    ...