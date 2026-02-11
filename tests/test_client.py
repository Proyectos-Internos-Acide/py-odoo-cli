import unittest
from unittest.mock import MagicMock, patch

import xmlrpc.client

from odoo_cli.client import OdooClient
from odoo_cli.exceptions import (
    OdooClientError,
    OdooConnectionError,
    OdooExecutionError,
    OdooFaultError,
)


def _mock_config():
    return {
        "ODOO_URL": "http://test",
        "ODOO_DB": "db",
        "ODOO_USER": "user",
        "ODOO_PASSWORD": "pass",
        "ODOO_VERIFY_SSL": False,
        "ODOO_TIMEOUT": 60,
    }


class TestOdooClient(unittest.TestCase):
    @patch("odoo_cli.client.Config")
    @patch("xmlrpc.client.ServerProxy")
    def test_connect(self, mock_server, mock_config):
        for k, v in _mock_config().items():
            setattr(mock_config, k, v)
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_server.return_value = mock_common

        client = OdooClient()
        uid = client.connect()

        self.assertEqual(uid, 1)
        mock_common.authenticate.assert_called_with("db", "user", "pass", {})

    @patch("odoo_cli.client.Config")
    @patch("xmlrpc.client.ServerProxy")
    def test_connect_auth_fails_raises_odoo_connection_error(self, mock_server, mock_config):
        """Si authenticate devuelve 0, se lanza OdooConnectionError."""
        for k, v in _mock_config().items():
            setattr(mock_config, k, v)

        mock_common = MagicMock()
        mock_common.authenticate.return_value = 0
        mock_server.return_value = mock_common

        client = OdooClient()
        with self.assertRaises(OdooConnectionError) as ctx:
            client.connect()
        self.assertIn("Authentication failed", str(ctx.exception))

    @patch("odoo_cli.client.Config")
    @patch("xmlrpc.client.ServerProxy")
    def test_connect_network_error_raises_odoo_connection_error(self, mock_server, mock_config):
        """Si hay error de red en connect, se lanza OdooConnectionError."""
        for k, v in _mock_config().items():
            setattr(mock_config, k, v)

        mock_common = MagicMock()
        mock_common.authenticate.side_effect = ConnectionError("Network unreachable")
        mock_server.return_value = mock_common

        client = OdooClient()
        with self.assertRaises(OdooConnectionError) as ctx:
            client.connect()
        self.assertIn("Could not connect", str(ctx.exception))

    @patch("odoo_cli.client.Config")
    @patch("xmlrpc.client.ServerProxy")
    def test_execute_fault_raises_odoo_fault_error(self, mock_server, mock_config):
        """Si Odoo devuelve Fault (xmlrpc), se lanza OdooFaultError con fault_code y fault_string."""
        for k, v in _mock_config().items():
            setattr(mock_config, k, v)

        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_models.execute_kw.side_effect = xmlrpc.client.Fault(1, "Access denied")
        mock_server.side_effect = [mock_common, mock_models]

        client = OdooClient()
        client.connect()
        with self.assertRaises(OdooFaultError) as ctx:
            client.execute("res.partner", "read", [1])
        self.assertEqual(ctx.exception.fault_code, 1)
        self.assertEqual(ctx.exception.fault_string, "Access denied")
        self.assertIn("Access denied", str(ctx.exception))

    @patch("odoo_cli.client.Config")
    @patch("xmlrpc.client.ServerProxy")
    def test_execute_generic_error_raises_odoo_execution_error(self, mock_server, mock_config):
        """Si execute_kw lanza otra excepción, se lanza OdooExecutionError."""
        for k, v in _mock_config().items():
            setattr(mock_config, k, v)

        mock_common = MagicMock()
        mock_common.authenticate.return_value = 1
        mock_models = MagicMock()
        mock_models.execute_kw.side_effect = TimeoutError("Timeout")
        mock_server.side_effect = [mock_common, mock_models]

        client = OdooClient()
        client.connect()
        with self.assertRaises(OdooExecutionError) as ctx:
            client.execute("res.partner", "read", [1])
        self.assertIn("Timeout", str(ctx.exception))


class TestExceptionHierarchy(unittest.TestCase):
    """Todas las excepciones propias heredan de OdooClientError."""

    def test_odoo_connection_error_is_odoo_client_error(self):
        self.assertIsInstance(OdooConnectionError("x"), OdooClientError)

    def test_odoo_fault_error_is_odoo_client_error(self):
        self.assertIsInstance(OdooFaultError("x"), OdooClientError)

    def test_odoo_execution_error_is_odoo_client_error(self):
        self.assertIsInstance(OdooExecutionError("x"), OdooClientError)


if __name__ == "__main__":
    unittest.main()
