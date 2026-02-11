import os
from urllib.parse import urlparse

from dotenv import load_dotenv

from .exceptions import OdooConfigError

load_dotenv()


def _parse_timeout(value: str | None) -> int:
    """Parse ODOO_TIMEOUT to int; default 60 seconds."""
    if value is None or value.strip() == "":
        return 60
    try:
        n = int(value.strip())
        return max(1, min(n, 3600))  # clamp 1-3600
    except ValueError:
        return 60


class Config:
    ODOO_URL = os.getenv("ODOO_URL")
    ODOO_DB = os.getenv("ODOO_DB")
    ODOO_USER = os.getenv("ODOO_USER")
    ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")
    ODOO_VERIFY_SSL = os.getenv("ODOO_VERIFY_SSL", "False").lower() == "true"
    ODOO_TIMEOUT = _parse_timeout(os.getenv("ODOO_TIMEOUT"))

    @classmethod
    def validate(cls) -> None:
        missing = []
        if not cls.ODOO_URL or not cls.ODOO_URL.strip():
            missing.append("ODOO_URL")
        if not cls.ODOO_DB or not str(cls.ODOO_DB).strip():
            missing.append("ODOO_DB")
        if not cls.ODOO_USER or not str(cls.ODOO_USER).strip():
            missing.append("ODOO_USER")
        if not cls.ODOO_PASSWORD:
            missing.append("ODOO_PASSWORD")

        if missing:
            raise OdooConfigError(f"Missing environment variables: {', '.join(missing)}")

        url = (cls.ODOO_URL or "").strip()
        if url:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                raise OdooConfigError(
                    "ODOO_URL must use http or https scheme."
                )
            if not parsed.netloc:
                raise OdooConfigError("ODOO_URL must contain a valid host.")
