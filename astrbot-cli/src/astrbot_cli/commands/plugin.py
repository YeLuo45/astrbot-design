"""Plugin management commands - install, list, uninstall, update, search."""

import typer
import requests
from rich.console import Console
from rich.table import Table
from typing import Optional

console = Console()
app = typer.Typer(help="Manage AstrBot plugins")


@app.command()
def install(
    plugin_id: str = typer.Argument(..., help="Plugin ID to install"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AstrBot API URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API Key"),
):
    """Install a plugin from registry or URL."""
    console.print(f"[bold blue]Installing plugin:[/bold blue] {plugin_id}")

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = requests.post(
            f"{api_url}/api/plugins/install",
            json={"plugin_id": plugin_id},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        console.print(f"[bold green]Successfully installed:[/bold green] {plugin_id}")
    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]Error:[/bold red] Cannot connect to {api_url}")
        console.print("Make sure AstrBot is running and the API is enabled.")
        raise typer.Exit(code=1)
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]HTTP Error:[/bold red] {e.response.status_code} - {e.response.text}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def list(
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AstrBot API URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API Key"),
):
    """List installed plugins."""
    console.print("[bold blue]Fetching installed plugins...[/bold blue]")

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = requests.get(
            f"{api_url}/api/plugins",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        plugins = response.json()

        if not plugins:
            console.print("[yellow]No plugins installed.[/yellow]")
            return

        table = Table(title="Installed Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Author", style="magenta")
        table.add_column("Description", style="white")

        for plugin in plugins:
            table.add_row(
                plugin.get("name", "unknown"),
                plugin.get("version", "0.0.0"),
                plugin.get("author", "unknown"),
                plugin.get("description", ""),
            )

        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(plugins)} plugin(s)")

    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]Error:[/bold red] Cannot connect to {api_url}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def uninstall(
    plugin_id: str = typer.Argument(..., help="Plugin ID to uninstall"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AstrBot API URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API Key"),
):
    """Uninstall a plugin."""
    console.print(f"[bold yellow]Uninstalling plugin:[/bold yellow] {plugin_id}")

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = requests.post(
            f"{api_url}/api/plugins/uninstall",
            json={"plugin_id": plugin_id},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        console.print(f"[bold green]Successfully uninstalled:[/bold green] {plugin_id}")

    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]Error:[/bold red] Cannot connect to {api_url}")
        raise typer.Exit(code=1)
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]HTTP Error:[/bold red] {e.response.status_code} - {e.response.text}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def update(
    plugin_id: str = typer.Argument(..., help="Plugin ID to update"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AstrBot API URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API Key"),
):
    """Update a plugin to latest version."""
    console.print(f"[bold blue]Updating plugin:[/bold blue] {plugin_id}")

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = requests.post(
            f"{api_url}/api/plugins/update",
            json={"plugin_id": plugin_id},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        console.print(f"[bold green]Successfully updated:[/bold green] {plugin_id}")

    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]Error:[/bold red] Cannot connect to {api_url}")
        raise typer.Exit(code=1)
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]HTTP Error:[/bold red] {e.response.status_code} - {e.response.text}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AstrBot API URL"),
):
    """Search plugins in marketplace."""
    console.print(f"[bold blue]Searching plugins for:[/bold blue] '{query}'")

    try:
        response = requests.get(
            f"{api_url}/api/marketplace/search",
            params={"q": query},
            timeout=10,
        )
        response.raise_for_status()
        results = response.json()

        if not results:
            console.print("[yellow]No plugins found.[/yellow]")
            return

        table = Table(title=f"Search Results for '{query}'")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Author", style="magenta")
        table.add_column("Downloads", style="blue")

        for plugin in results:
            table.add_row(
                plugin.get("name", "unknown"),
                plugin.get("version", "0.0.0"),
                plugin.get("author", "unknown"),
                str(plugin.get("downloads", 0)),
            )

        console.print(table)
        console.print(f"\n[bold]Total results:[/bold] {len(results)}")

    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]Error:[/bold red] Cannot connect to {api_url}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
