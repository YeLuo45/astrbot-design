"""Configuration management commands - get, set, export, import."""

import typer
import json
import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from typing import Optional, Any

console = Console()
app = typer.Typer(help="Manage AstrBot configuration")


@app.command()
def get(
    key: Optional[str] = typer.Argument(None, help="Config key (omit to list all)"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AstrBot API URL"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, yaml"),
):
    """Get configuration value(s)."""
    console.print(f"[bold blue]Fetching configuration...[/bold blue]")

    try:
        import requests
        response = requests.get(
            f"{api_url}/api/config",
            timeout=10,
        )
        response.raise_for_status()
        config = response.json()

        if key:
            value = config.get(key)
            if value is None:
                console.print(f"[yellow]Key '{key}' not found.[/yellow]")
                raise typer.Exit(code=1)

            if format == "yaml":
                output = yaml.dump({key: value}, default_flow_style=False)
            else:
                output = json.dumps({key: value}, indent=2)
            console.print(output)
        else:
            # List all
            if format == "yaml":
                output = yaml.dump(config, default_flow_style=False)
            else:
                output = json.dumps(config, indent=2)
            console.print(output)

    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]Error:[/bold red] Cannot connect to {api_url}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def set(
    key: str = typer.Argument(..., help="Config key"),
    value: str = typer.Argument(..., help="Config value"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AstrBot API URL"),
):
    """Set a configuration value."""
    console.print(f"[bold blue]Setting {key} = {value}[/bold blue]")

    try:
        import requests
        response = requests.put(
            f"{api_url}/api/config/{key}",
            json={"value": value},
            timeout=10,
        )
        response.raise_for_status()
        console.print(f"[bold green]Successfully updated:[/bold green] {key}")

    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]Error:[/bold red] Cannot connect to {api_url}")
        raise typer.Exit(code=1)
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]HTTP Error:[/bold red] {e.response.status_code}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def export(
    output_file: str = typer.Argument("astrbot-config.json", help="Output file path"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AstrBot API URL"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, yaml"),
):
    """Export configuration to file."""
    console.print(f"[bold blue]Exporting configuration to:[/bold blue] {output_file}")

    try:
        import requests
        response = requests.get(
            f"{api_url}/api/config",
            timeout=10,
        )
        response.raise_for_status()
        config = response.json()

        output_path = Path(output_file)
        if format == "yaml":
            output_path = output_path.with_suffix(".yaml")
            content = yaml.dump(config, default_flow_style=False)
        else:
            output_path = output_path.with_suffix(".json")
            content = json.dumps(config, indent=2)

        output_path.write_text(content)
        console.print(f"[bold green]Configuration exported to:[/bold green] {output_path}")

    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]Error:[/bold red] Cannot connect to {api_url}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def import_config(
    input_file: str = typer.Argument(..., help="Input file path"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AstrBot API URL"),
    merge: bool = typer.Option(True, "--merge/--replace", help="Merge with existing or replace"),
):
    """Import configuration from file."""
    console.print(f"[bold blue]Importing configuration from:[/bold blue] {input_file}")

    input_path = Path(input_file)
    if not input_path.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {input_file}")
        raise typer.Exit(code=1)

    try:
        content = input_path.read_text()

        if input_path.suffix in (".yaml", ".yml"):
            config = yaml.safe_load(content)
        else:
            config = json.loads(content)

        import requests
        response = requests.post(
            f"{api_url}/api/config/import",
            json={"config": config, "merge": merge},
            timeout=30,
        )
        response.raise_for_status()
        console.print(f"[bold green]Configuration imported successfully[/bold green]")

    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]Error:[/bold red] Cannot connect to {api_url}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
