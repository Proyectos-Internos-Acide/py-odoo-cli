import os
from dotenv import load_dotenv

from .exceptions import OdooConfigError

load_dotenv()


class Config:
    ODOO_URL = os.getenv('ODOO_URL')
    ODOO_DB = os.getenv('ODOO_DB')
    ODOO_USER = os.getenv('ODOO_USER')
    ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')
    ODOO_VERIFY_SSL = os.getenv('ODOO_VERIFY_SSL', 'False').lower() == 'true'

    @classmethod
    def validate(cls) -> None:
        missing = []
        if not cls.ODOO_URL:
            missing.append('ODOO_URL')
        if not cls.ODOO_DB:
            missing.append('ODOO_DB')
        if not cls.ODOO_USER:
            missing.append('ODOO_USER')
        if not cls.ODOO_PASSWORD:
            missing.append('ODOO_PASSWORD')

        if missing:
            raise OdooConfigError(f"Missing environment variables: {', '.join(missing)}")
