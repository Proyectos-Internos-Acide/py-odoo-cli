import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ODOO_URL = os.getenv('ODOO_URL')
    ODOO_DB = os.getenv('ODOO_DB')
    ODOO_USER = os.getenv('ODOO_USER')
    ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

    @classmethod
    def validate(cls) -> None:
        missing = []
        if not cls.ODOO_URL: missing.append('ODOO_URL')
        if not cls.ODOO_DB: missing.append('ODOO_DB')
        if not cls.ODOO_USER: missing.append('ODOO_USER')
        if not cls.ODOO_PASSWORD: missing.append('ODOO_PASSWORD')
        
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")
