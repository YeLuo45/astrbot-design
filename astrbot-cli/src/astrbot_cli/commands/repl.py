"""REPL command implementation."""

import asyncio
import sys
from typing import Optional

import requests
from rich.console import Console
from rich.markdown import Markdown


console = Console()


def run_repl(agent_id: str, host: str, port: int):
    """Run interactive REPL session."""
    base_url = f"http://{host}:{port}"

    console.print(f"[bold green]AstrBot REPL[/bold green]")
    console.print(f"Connecting to {base_url}")
    console.print("Type [bold]exit[/bold] to quit, [bold]help[/bold] for commands\n")

    while True:
        try:
            user_input = console.input("[blue]>[/blue] ").strip()

            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[yellow]Goodbye![/yellow]")
                break

            if not user_input:
                continue

            if user_input.lower() == "help":
                console.print("[bold]Commands:[/bold]")
                console.print("  exit, quit, q - Exit REPL")
                console.print("  help - Show this help")
                console.print("  clear - Clear screen")
                continue

            if user_input.lower() == "clear":
                console.clear()
                continue

            # Call Agent API
            try:
                response = requests.post(
                    f"{base_url}/api/agents/{agent_id}/call",
                    json={"input": user_input},
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                result = data.get("response", "No response")
                console.print(f"[green]{result}[/green]\n")

            except requests.exceptions.ConnectionError:
                console.print(f"[red]Error: Cannot connect to AstrBot at {base_url}[/red]")
                console.print("[yellow]Make sure AstrBot is running and the API is enabled.[/yellow]\n")
            except requests.exceptions.Timeout:
                console.print("[red]Error: Request timed out[/red]\n")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]\n")

        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
            break
