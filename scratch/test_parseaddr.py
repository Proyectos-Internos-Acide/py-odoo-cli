import sys
import os
from dotenv import load_dotenv
import xmlrpc.client

load_dotenv()

URL = os.getenv("ODOO_URL")
DB = os.getenv("ODOO_DB")
USER = os.getenv("ODOO_USER")
PASS = os.getenv("ODOO_PASSWORD")

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

test_code = """
from email.utils import parseaddr

if record.email_from:
    display_name, email_addr = parseaddr(record.email_from)
    # Log test
    record.message_post(body=f"TEST PARSEADDR: Name='{display_name}' Email='{email_addr}'")
"""

print("Testing parseaddr in server action...")
# Let's check server action 584 execution or test
sa = models.execute_kw(DB, uid, PASS, 'ir.actions.server', 'read', [[584]], {'fields': ['id', 'name', 'code']})
print("Current SA 584 Name:", sa[0]['name'])
