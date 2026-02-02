#!/usr/bin/env python3
import argparse
import sys
from odoo_cli import OdooClient

def main():
    parser = argparse.ArgumentParser(description="CLI tool to interact with Odoo via XML-RPC")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # Command: test_connection
    subparsers.add_parser("test_connection", help="Test connection to Odoo")

    # Command: list
    list_parser = subparsers.add_parser("list", help="List records from a model")
    list_parser.add_argument("model", help="Odoo model name (e.g. res.partner)")
    list_parser.add_argument("--limit", type=int, default=10, help="Limit results")
    list_parser.add_argument("--fields", help="Comma separated fields (e.g. name,email)")

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        sys.exit(1)

    try:
        client = OdooClient()
        
        if args.action == "test_connection":
            uid = client.connect()
            print(f"✅ Automatically connected! User ID: {uid}")
            
        elif args.action == "list":
            fields = args.fields.split(',') if args.fields else ['name']
            records = client.search_read(args.model, fields=fields, limit=args.limit)
            
            print(f"Found {len(records)} records in {args.model}:")
            print("-" * 40)
            for rec in records:
                print(rec)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
