# Tohalino - Electronic Invoicing

Technical guide and scripts for managing Peruvian Electronic Invoicing (FE).

## FE Environment
- **Provider**: SUNAT (Direct)
- **Status**: Production (Wait until verified)

## Available Scripts
- [verify_fe_config.py](./verify_fe_config.py): Module and basic configuration check.
- [verify_fe_details.py](./verify_fe_details.py): SOL credentials and Ubigeo verification.
- [cancel_invoices.py](./cancel_invoices.py): Reverses invoices via Credit Notes.
- [cleanup_records.py](./cleanup_records.py): Deletes invoices and credit notes (Use with caution).
- [fe_logic_guide.py](./fe_logic_guide.py): Code overview of the FE implementation.
