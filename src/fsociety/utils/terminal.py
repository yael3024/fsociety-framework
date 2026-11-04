"""Terminal presentation helpers."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()
ART = """[bold red]███████╗███████╗ ██████╗  ██████╗██╗███████╗████████╗██╗   ██╗[/bold red]
[bold white]██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝[/bold white]
[bold red]█████╗  ███████╗██║   ██║██║     ██║█████╗     ██║    ╚████╔╝ [/bold red]
[bold white]██╔══╝  ╚════██║██║   ██║██║     ██║██╔══╝     ██║     ╚██╔╝  [/bold white]
[bold red]███████╗███████║╚██████╔╝╚██████╗██║██║        ██║      ██║   [/bold red]
[bold white]╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚═╝╚═╝        ╚═╝      ╚═╝   [/bold white]"""


def banner() -> None:
    console.print(Panel(Text.from_markup(ART), subtitle="DEFENSIVE SECURITY TOOLKIT", border_style="red"))
