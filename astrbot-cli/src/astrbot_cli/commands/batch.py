"""Batch operations - install/uninstall/update multiple plugins at once."""

import typer
import requests
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import List

console = Console()
app = typer.Typer(help="Batch operations on multiple plugins")


def read_plugin_list(file_path: str) -> List[str]:
    """Read plugin IDs from file (one per line)."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text()
    plugins = [
        line.strip() for line in content.splitlines()
        if line.strip() and not line.startswith("#")
    ]
    return plugins


@app.command(name="install")
def batch_install(
    file: str = typer.Argument(..., help="File containing plugin list (one ID per line)"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AstrBot API URL"),
    api_key: str = typer.Option("", "--api-key", help="API Key"),
):
    """Batch install plugins from a list file."""
    console.print(f"[bold blue]Reading plugin list from:[/bold blue] {file}")

    try:
        plugins = read_plugin_list(file)
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print(f"[bold]Total plugins to install:[/bold] {len(plugins)}")

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    success = []
    failed = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Installing plugins...", total=len(plugins))

        for plugin_id in plugins:
            try:
                response = requests.post(
                    f"{api_url}/api/plugins/install",
                    json={"plugin_id": plugin_id},
                    headers=headers,
                    timeout=30,
                )
                response.raise_for_status()
                success.append(plugin_id)
            except Exception as e:
                failed.append((plugin_id, str(e)))

            progress.update(task, advance=1)

    # Summary
    console.print("\n[bold]Batch Install Summary[/bold]")
    if success:
        console.print(f"[green]Success:[/green] {len(success)} plugin(s)")
        for p in success:
            console.print(f"  - {p}")
    if failed:
        console.print(f"[red]Failed:[/red] {len(failed)} plugin(s)")
        for p, err in failed:
            console.print(f"  - {p}: {err}")


@app.command(name="uninstall")
def batch_uninstall(
    file: str = typer.Argument(..., help="File containing plugin list to uninstall"),
    api_url: str = typer.Option("http://localhost:8000", "--api-url", help="AstrBot API URL"),
    api_key: str = typer.Option("", "--api-key", help="API Key"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Batch uninstall plugins from a list file."""
    try:
        plugins = read_plugin_list(file)
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    if not force:
        console.print(f"[bold yellow]About to uninstall {len(plugins)} plugins:[/bold yellow]")
        for p in plugins:
            console.print(f"  - {p}")
        confirm = console.input("\nProceed? [y/N] ")
        if confirm.lower() != "y":
            console.print("[yellow]Cancelled.[/yellow]")
            return

    console.print(f"[bold]Total plugins to uninstall:[/bold] {len(plugins)}")

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    success = []
    failed = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Uninstalling plugins...", total=len(plugins))

        for plugin_id in plugins:
            try:
                response = requests.post(
                    f"{api_url}/api/plugins/uninstall",
                    json={"plugin_id": plugin_id},
                    headers=headers,
                    timeout=30,
                )
                response.raise_for_status()
                success.append(plugin_id)
            except Exception as e:
                failed.append((plugin_id, str(e)))

            progress.update(task, advance=1)

    # Summary
    console.print("\n[bold]Batch Uninstall Summary[/bold]")
    if success:
        console.print(f"[green]Success:[/green] {len(success)} plugin(s)")
    if failed:
        console.print(f"[red]Failed:[/red] {len(failed)} plugin(s)")
        for p, err in failed:
            console.print(f"  - {p}: {err}")


@app.command()
def list_file(file: str = typer.Argument(..., help="File containing plugin list")):
    """Preview plugins in a list file without installing."""
    try:
        plugins = read_plugin_list(file)
        console.print(f"[bold]Plugins in {file}:[/bold] {len(plugins)}")
        for p in plugins:
            console.print(f"  - {p}")
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
