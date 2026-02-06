from .client import OdooClient
from .exceptions import (
    OdooClientError,
    OdooConfigError,
    OdooConnectionError,
    OdooExecutionError,
    OdooFaultError,
)

__all__ = [
    "OdooClient",
    "OdooClientError",
    "OdooConfigError",
    "OdooConnectionError",
    "OdooExecutionError",
    "OdooFaultError",
]
