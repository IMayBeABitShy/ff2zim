"""
Exception definitions.
"""

class DirectoryNotEmpty(Exception):
    """
    Exception raised when a directory is not empty.
    """
    pass


class AlreadyExists(Exception):
    """
    Exception raised when a path already exists.
    """
    pass


class NotAValidProject(Exception):
    """
    Exception raised when a path does not refer to a valid project.
    """
    pass


class NotAValidTarget(Exception):
    """
    Exception raised when something is not a valid target.
    """
    pass
