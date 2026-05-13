"""AstrBot CLI - Main entry point."""

import typer
from rich.console import Console

app = typer.Typer(
    name="astrbot",
    help="AstrBot CLI - Modern command line tools for AstrBot development",
    add_completion=False,
)

console = Console()


@app.callback()
def callback():
    """AstrBot CLI - Modern command line tools."""
    pass


@app.command()
def repl(
    agent_id: str = typer.Option("default", "--agent", "-a", help="Agent ID to interact with"),
    host: str = typer.Option("localhost", "--host", "-h", help="AstrBot API host"),
    port: int = typer.Option(8000, "--port", "-p", help="AstrBot API port"),
):
    """Start an interactive REPL session with an Agent."""
    from .commands.repl import run_repl
    run_repl(agent_id, host, port)


@app.command()
def version():
    """Show AstrBot CLI version."""
    from . import __version__
    console.print(f"[bold green]AstrBot CLI[/bold green] v{__version__}")


if __name__ == "__main__":
    app()
