"""Errors
docker-pretty-ps rrrors that might be thrown when problems happen.

"""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class BadResponseDockerEngine(Error):
    """Raised when the Docker Engine does not supply a propper response"""
    pass
