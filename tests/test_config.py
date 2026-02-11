import unittest
from unittest.mock import patch

from odoo_cli.config import Config
from odoo_cli.exceptions import OdooConfigError


class TestConfig(unittest.TestCase):
    """Tests para Config.validate() y OdooConfigError."""

    @patch.object(Config, "ODOO_URL", "https://test.odoo.com")
    @patch.object(Config, "ODOO_DB", "testdb")
    @patch.object(Config, "ODOO_USER", "user")
    @patch.object(Config, "ODOO_PASSWORD", "secret")
    def test_validate_success(self):
        """Con todas las variables definidas no debe lanzar."""
        Config.validate()

    @patch.object(Config, "ODOO_URL", None)
    @patch.object(Config, "ODOO_DB", None)
    @patch.object(Config, "ODOO_USER", None)
    @patch.object(Config, "ODOO_PASSWORD", None)
    def test_validate_missing_all_raises_odoo_config_error(self):
        """Faltan todas las variables -> OdooConfigError."""
        with self.assertRaises(OdooConfigError) as ctx:
            Config.validate()
        self.assertIn("Missing environment variables", str(ctx.exception))
        self.assertIn("ODOO_URL", str(ctx.exception))

    @patch.object(Config, "ODOO_URL", "http://x")
    @patch.object(Config, "ODOO_DB", "db")
    @patch.object(Config, "ODOO_USER", None)
    @patch.object(Config, "ODOO_PASSWORD", "pass")
    def test_validate_missing_some_raises_odoo_config_error(self):
        """Faltan solo algunas variables -> OdooConfigError."""
        with self.assertRaises(OdooConfigError) as ctx:
            Config.validate()
        self.assertIn("ODOO_USER", str(ctx.exception))

    def test_odoo_config_error_is_value_error(self):
        """OdooConfigError debe ser capturable como ValueError."""
        with self.assertRaises(ValueError):
            raise OdooConfigError("Missing ODOO_URL")

    @patch.object(Config, "ODOO_URL", "ftp://invalid.example.com")
    @patch.object(Config, "ODOO_DB", "db")
    @patch.object(Config, "ODOO_USER", "user")
    @patch.object(Config, "ODOO_PASSWORD", "pass")
    def test_validate_invalid_url_scheme_raises_odoo_config_error(self):
        """URL con esquema distinto de http/https lanza OdooConfigError."""
        with self.assertRaises(OdooConfigError) as ctx:
            Config.validate()
        self.assertIn("http or https", str(ctx.exception))
