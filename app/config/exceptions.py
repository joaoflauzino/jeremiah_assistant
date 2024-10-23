class RepositoryError(Exception):
    """Base exception class for repository errors."""
    pass

class DatabaseError(RepositoryError):
    """Raised when a database operation fails."""
    pass

class ServiceError(Exception):
    """Raised when a Service operation fails."""
    pass