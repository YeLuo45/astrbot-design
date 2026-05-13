"""Scaffold new project (plugin/agent/adapter)."""

import os
import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
app = typer.Typer(help="Create new AstrBot projects from templates")


TEMPLATES = {
    "plugin": "plugin_basic",
    "agent": "agent_conversational",
    "adapter": "adapter_basic",
}


@app.command()
def plugin(
    name: str = typer.Argument(..., help="Plugin name (e.g. my-plugin)"),
    template: str = typer.Option("basic", "--template", "-t", help="Template type: basic, advanced"),
    output_dir: str = typer.Option(".", "--output", "-o", help="Output directory"),
):
    """Create a new AstrBot plugin."""
    _create_project("plugin", name, template, output_dir)


@app.command()
def agent(
    name: str = typer.Argument(..., help="Agent name (e.g. my-agent)"),
    template: str = typer.Option("conversational", "--template", "-t", help="Template type: conversational, task-oriented"),
    output_dir: str = typer.Option(".", "--output", "-o", help="Output directory"),
):
    """Create a new AstrBot agent."""
    _create_project("agent", name, template, output_dir)


@app.command()
def adapter(
    name: str = typer.Argument(..., help="Adapter name (e.g. discord-adapter)"),
    platform: str = typer.Option("generic", "--platform", "-p", help="Platform: discord, telegram, slack"),
    output_dir: str = typer.Option(".", "--output", "-o", help="Output directory"),
):
    """Create a new platform adapter."""
    _create_project("adapter", name, platform, output_dir)


def _create_project(project_type: str, name: str, template: str, output_dir: str):
    """Internal function to create a project from template."""
    template_name = TEMPLATES.get(project_type, "plugin_basic")
    template_path = Path(__file__).parent.parent / "templates" / template_name

    if not template_path.exists():
        console.print(f"[red]Template not found: {template_name}[/red]")
        console.print(f"Available templates: {', '.join(TEMPLATES.values())}")
        raise typer.Exit(code=1)

    dest_path = Path(output_dir) / name

    if dest_path.exists():
        console.print(f"[red]Error: Directory already exists: {dest_path}[/red]")
        raise typer.Exit(code=1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating project...", total=None)

        # Copy template
        shutil.copytree(template_path, dest_path)

        # Replace placeholders
        _replace_placeholders(dest_path, name, project_type)

        progress.update(task, completed=True)

    console.print(f"[bold green]Success![/bold green] Created {project_type} at {dest_path}")
    console.print(f"\nTo get started:")
    console.print(f"  cd {dest_path}")
    console.print(f"  astrbot plugin install -e .")


def _replace_placeholders(path: Path, name: str, project_type: str):
    """Replace {{name}} and {{type}} placeholders in template files."""
    for root, dirs, files in os.walk(path):
        for filename in files:
            filepath = Path(root) / filename
            try:
                content = filepath.read_text()
                updated = content.replace("{{plugin_name}}", name)
                updated = updated.replace("{{project_type}}", project_type)
                filepath.write_text(updated)
            except Exception:
                pass  # Skip binary files
