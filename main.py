#!/usr/bin/env python3
import sys
import typer
from typing import Optional
from odoo_cli import OdooClient

app = typer.Typer(help="CLI tool to interact with Odoo via XML-RPC")

def get_client():
    try:
        return OdooClient()
    except Exception as e:
        typer.secho(f"❌ Error initializing client: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def test_connection():
    """Test connection to Odoo"""
    client = get_client()
    try:
        uid = client.connect()
        typer.secho(f"✅ Automatically connected! User ID: {uid}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"❌ Connection failed: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command("list")
def list_records(
    model: str = typer.Argument(..., help="Odoo model name (e.g. res.partner)"),
    limit: int = typer.Option(10, help="Limit results"),
    fields: Optional[str] = typer.Option(None, help="Comma separated fields (e.g. name,email)")
):
    """List records from a model"""
    client = get_client()
    try:
        field_list = fields.split(',') if fields else ['name']
        records = client.search_read(model, fields=field_list, limit=limit)
        
        typer.secho(f"Found {len(records)} records in {model}:", fg=typer.colors.BLUE)
        typer.echo("-" * 40)
        for rec in records:
            typer.echo(rec)
    except Exception as e:
        typer.secho(f"❌ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def list_modules():
    """List installed modules"""
    client = get_client()
    try:
        typer.secho("📦 Fetching installed modules...", fg=typer.colors.YELLOW)
        modules = client.search_read(
            'ir.module.module', 
            domain=[['state', '=', 'installed']], 
            fields=['name', 'shortdesc', 'author', 'installed_version'],
            order='name'
        )
        typer.echo("-" * 80)
        typer.echo(f"{'Name':<30} | {'Version':<15} | {'Description'}")
        typer.echo("-" * 80)
        for m in modules:
            name = m.get('name') or ''
            version = m.get('installed_version') or ''
            desc = m.get('shortdesc') or ''
            typer.echo(f"{name:<30} | {version:<15} | {desc}")
        typer.echo("-" * 80)
        typer.echo(f"Total installed modules: {len(modules)}")
    except Exception as e:
        typer.secho(f"❌ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def list_config():
    """List system parameters"""
    client = get_client()
    try:
        typer.secho("⚙️  Fetching system parameters...", fg=typer.colors.YELLOW)
        params = client.search_read(
            'ir.config_parameter', 
            domain=[], 
            fields=['key', 'value'],
            order='key'
        )
        typer.echo("-" * 80)
        typer.echo(f"{'Key':<40} | {'Value'}")
        typer.echo("-" * 80)
        for p in params:
            key = p.get('key') or ''
            value = p.get('value') or ''
            # Truncate long values
            if len(value) > 50:
                value = value[:47] + "..."
            typer.echo(f"{key:<40} | {value}")
        typer.echo("-" * 80)
    except Exception as e:
        typer.secho(f"❌ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
