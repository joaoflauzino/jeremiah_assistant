class RepositoryError(Exception):
    """Base exception class for repository errors."""

    ...


class DatabaseError(RepositoryError):
    """Raised when a database operation fails."""

    ...
