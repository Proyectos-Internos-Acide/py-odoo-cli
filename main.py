#!/usr/bin/env python3
import json
from typing import Optional

import typer
from odoo_cli import OdooClient
from odoo_cli.exceptions import (
    OdooConfigError,
    OdooConnectionError,
    OdooExecutionError,
    OdooFaultError,
)

app = typer.Typer(help="CLI tool to interact with Odoo via XML-RPC")


def get_client() -> OdooClient:
    try:
        return OdooClient()
    except OdooConfigError as e:
        typer.secho(f"Config error: {e}", fg=typer.colors.RED)
        typer.secho("Check your .env file (ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD).", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Error initializing client: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


def _handle_odoo_errors(e: Exception) -> None:
    if isinstance(e, OdooConnectionError):
        typer.secho(f"Connection error: {e}", fg=typer.colors.RED)
        typer.secho("Check credentials and that Odoo is reachable.", fg=typer.colors.YELLOW)
    elif isinstance(e, OdooFaultError):
        typer.secho(f"Odoo error: {e.fault_string}", fg=typer.colors.RED)
        if e.fault_code is not None:
            typer.secho(f"Fault code: {e.fault_code}", fg=typer.colors.YELLOW)
    elif isinstance(e, OdooExecutionError):
        typer.secho(f"Execution error: {e}", fg=typer.colors.RED)
    else:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
    raise typer.Exit(code=1)


def _parse_domain(domain_str: Optional[str]) -> list:
    if not domain_str or not domain_str.strip():
        return []
    try:
        return json.loads(domain_str)
    except json.JSONDecodeError:
        typer.secho("Invalid --domain: must be valid JSON (e.g. [['is_company','=',true]]).", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def test_connection() -> None:
    """Test connection to Odoo."""
    client = get_client()
    try:
        uid = client.connect()
        typer.secho(f"Connected. User ID: {uid}", fg=typer.colors.GREEN)
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        _handle_odoo_errors(e)


@app.command("list")
def list_records(
    model: str = typer.Argument(..., help="Odoo model name (e.g. res.partner)"),
    limit: int = typer.Option(10, help="Limit results"),
    fields: Optional[str] = typer.Option(None, help="Comma-separated fields (e.g. name,email)"),
    domain: Optional[str] = typer.Option(None, help="Domain as JSON (e.g. [['is_company','=',true]])"),
    output: str = typer.Option("text", help="Output format: text, json, or csv"),
) -> None:
    """List records from a model."""
    client = get_client()
    try:
        field_list = [f.strip() for f in fields.split(",")] if fields else ["name"]
        domain_list = _parse_domain(domain)
        records = client.search_read(
            model,
            domain=domain_list if domain_list else None,
            fields=field_list,
            limit=limit,
        )
        if output == "json":
            typer.echo(json.dumps(records, default=str, indent=2))
            return
        if output == "csv":
            if not records:
                return
            headers = list(records[0].keys())
            typer.echo(",".join(headers))
            for rec in records:
                row = [str(rec.get(h, "")) for h in headers]
                typer.echo(",".join(row))
            return
        typer.secho(f"Found {len(records)} records in {model}:", fg=typer.colors.BLUE)
        typer.echo("-" * 40)
        for rec in records:
            typer.echo(rec)
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        _handle_odoo_errors(e)


@app.command()
def list_modules() -> None:
    """List installed modules."""
    client = get_client()
    try:
        typer.secho("Fetching installed modules...", fg=typer.colors.YELLOW)
        modules = client.search_read(
            "ir.module.module",
            domain=[["state", "=", "installed"]],
            fields=["name", "shortdesc", "author", "installed_version"],
            order="name",
        )
        typer.echo("-" * 80)
        typer.echo(f"{'Name':<30} | {'Version':<15} | {'Description'}")
        typer.echo("-" * 80)
        for m in modules:
            name = m.get("name") or ""
            version = m.get("installed_version") or ""
            desc = m.get("shortdesc") or ""
            typer.echo(f"{name:<30} | {version:<15} | {desc}")
        typer.echo("-" * 80)
        typer.echo(f"Total installed modules: {len(modules)}")
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        _handle_odoo_errors(e)


@app.command()
def list_config() -> None:
    """List system parameters."""
    client = get_client()
    try:
        typer.secho("Fetching system parameters...", fg=typer.colors.YELLOW)
        params = client.search_read(
            "ir.config_parameter",
            domain=[],
            fields=["key", "value"],
            order="key",
        )
        typer.echo("-" * 80)
        typer.echo(f"{'Key':<40} | {'Value'}")
        typer.echo("-" * 80)
        for p in params:
            key = p.get("key") or ""
            value = p.get("value") or ""
            if len(value) > 50:
                value = value[:47] + "..."
            typer.echo(f"{key:<40} | {value}")
        typer.echo("-" * 80)
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        _handle_odoo_errors(e)


@app.command()
def create(
    model: str = typer.Argument(..., help="Odoo model name (e.g. res.partner)"),
    data: str = typer.Option(..., "--data", "-d", help="JSON object with field values (e.g. '{\"name\":\"Test\"}')"),
) -> None:
    """Create a record in a model."""
    client = get_client()
    try:
        vals = json.loads(data)
        if not isinstance(vals, dict):
            typer.secho("--data must be a JSON object.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        new_id = client.create(model, vals)
        typer.secho(f"Created record in {model} with ID: {new_id}", fg=typer.colors.GREEN)
    except json.JSONDecodeError as e:
        typer.secho(f"Invalid JSON in --data: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        _handle_odoo_errors(e)


@app.command()
def write(
    model: str = typer.Argument(..., help="Odoo model name (e.g. res.partner)"),
    ids: str = typer.Argument(..., help="Comma-separated record IDs (e.g. 1,2,3)"),
    data: str = typer.Option(..., "--data", "-d", help="JSON object with field values to write"),
) -> None:
    """Update records in a model."""
    client = get_client()
    try:
        id_list = [int(i.strip()) for i in ids.split(",") if i.strip()]
        if not id_list:
            typer.secho("At least one ID is required.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        vals = json.loads(data)
        if not isinstance(vals, dict):
            typer.secho("--data must be a JSON object.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        client.write(model, id_list, vals)
        typer.secho(f"Updated {len(id_list)} record(s) in {model}.", fg=typer.colors.GREEN)
    except json.JSONDecodeError as e:
        typer.secho(f"Invalid JSON in --data: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except ValueError:
        typer.secho("IDs must be integers.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        _handle_odoo_errors(e)


@app.command()
def unlink(
    model: str = typer.Argument(..., help="Odoo model name (e.g. res.partner)"),
    ids: str = typer.Argument(..., help="Comma-separated record IDs to delete (e.g. 1,2,3)"),
) -> None:
    """Delete records from a model."""
    client = get_client()
    try:
        id_list = [int(i.strip()) for i in ids.split(",") if i.strip()]
        if not id_list:
            typer.secho("At least one ID is required.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        client.unlink(model, id_list)
        typer.secho(f"Deleted {len(id_list)} record(s) from {model}.", fg=typer.colors.GREEN)
    except ValueError:
        typer.secho("IDs must be integers.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except (OdooConnectionError, OdooFaultError, OdooExecutionError) as e:
        _handle_odoo_errors(e)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
