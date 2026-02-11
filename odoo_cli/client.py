import logging
import ssl
import xmlrpc.client
from typing import Any, Dict, List, Optional

from .config import Config
from .exceptions import (
    OdooConnectionError,
    OdooExecutionError,
    OdooFaultError,
)


class _TimeoutTransport(xmlrpc.client.Transport):
    """XML-RPC transport that applies a socket timeout to connections."""

    def __init__(self, timeout: int = 60, use_datetime: bool = False, use_builtin_types: bool = False):
        super().__init__(use_datetime=use_datetime, use_builtin_types=use_builtin_types)
        self._timeout = timeout

    def make_connection(self, host: str) -> Any:
        conn = super().make_connection(host)
        if hasattr(conn, "timeout"):
            conn.timeout = self._timeout
        return conn


class _TimeoutSafeTransport(xmlrpc.client.SafeTransport):
    """XML-RPC safe transport (HTTPS) with socket timeout."""

    def __init__(self, timeout: int = 60, use_datetime: bool = False, use_builtin_types: bool = False, context: Optional[ssl.SSLContext] = None):
        super().__init__(use_datetime=use_datetime, use_builtin_types=use_builtin_types, context=context)
        self._timeout = timeout

    def make_connection(self, host: str) -> Any:
        conn = super().make_connection(host)
        if hasattr(conn, "timeout"):
            conn.timeout = self._timeout
        return conn


class OdooClient:
    def __init__(self) -> None:
        Config.validate()
        self._base_url = (Config.ODOO_URL or "").strip().rstrip("/")
        self.db = Config.ODOO_DB
        self.username = Config.ODOO_USER
        self.password = Config.ODOO_PASSWORD
        self.uid: Optional[int] = None
        self.logger = logging.getLogger(__name__)
        self._timeout = Config.ODOO_TIMEOUT

        if Config.ODOO_VERIFY_SSL:
            self._context = ssl.create_default_context()
        else:
            self._context = ssl._create_unverified_context()

        if self._base_url.startswith("https://"):
            self._transport = _TimeoutSafeTransport(
                timeout=self._timeout,
                context=self._context,
            )
        else:
            self._transport = _TimeoutTransport(timeout=self._timeout)

        self._common_proxy: Optional[Any] = None
        self._object_proxy: Optional[Any] = None

    def _get_common(self) -> Any:
        if self._common_proxy is None:
            self._common_proxy = xmlrpc.client.ServerProxy(
                f"{self._base_url}/xmlrpc/2/common",
                transport=self._transport,
            )
        return self._common_proxy

    def _get_object(self) -> Any:
        if self._object_proxy is None:
            self._object_proxy = xmlrpc.client.ServerProxy(
                f"{self._base_url}/xmlrpc/2/object",
                transport=self._transport,
            )
        return self._object_proxy

    def connect(self) -> int:
        """Authenticate with Odoo and retrieve UID."""
        try:
            common = self._get_common()
            self.uid = int(common.authenticate(self.db, self.username, self.password, {}))
            if not self.uid:
                self.logger.error("Authentication failed for user: %s", self.username)
                raise OdooConnectionError("Authentication failed. Check your credentials.")
            self.logger.info("Successfully authenticated as user ID: %s", self.uid)
            return self.uid
        except OdooConnectionError:
            raise
        except Exception as e:
            self.logger.exception("Connection error")
            raise OdooConnectionError(f"Could not connect to Odoo: {e}") from e

    def execute(self, model: str, method: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a method on an Odoo model."""
        if not self.uid:
            self.connect()

        models = self._get_object()
        try:
            self.logger.debug(
                "Executing %s on model %s with args: %s kwargs: %s",
                method,
                model,
                args,
                kwargs,
            )
            return models.execute_kw(
                self.db,
                self.uid,
                self.password,
                model,
                method,
                args,
                kwargs,
            )
        except xmlrpc.client.Fault as e:
            self.logger.error("Odoo Fault: %s", e)
            raise OdooFaultError(
                f"Odoo Fault: {e.faultString}",
                fault_code=getattr(e, "faultCode", None),
                fault_string=getattr(e, "faultString", str(e)),
            ) from e
        except Exception as e:
            self.logger.error("Execution error: %s", e)
            raise OdooExecutionError(f"Execution error: {e}") from e

    def search_read(
        self,
        model: str,
        domain: Optional[List[Any]] = None,
        fields: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        order: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Helper for search_read method."""
        domain = domain or []
        kwargs: Dict[str, Any] = {}
        if fields:
            kwargs["fields"] = fields
        if limit is not None:
            kwargs["limit"] = limit
        if offset:
            kwargs["offset"] = offset
        if order:
            kwargs["order"] = order

        return self.execute(model, "search_read", domain, **kwargs)

    def create(self, model: str, vals: Dict[str, Any]) -> int:
        """Helper to create a record."""
        return int(self.execute(model, "create", vals))

    def write(self, model: str, ids: List[int], vals: Dict[str, Any]) -> bool:
        """Helper to update records."""
        return bool(self.execute(model, "write", ids, vals))

    def unlink(self, model: str, ids: List[int]) -> bool:
        """Helper to delete records."""
        return bool(self.execute(model, "unlink", ids))
