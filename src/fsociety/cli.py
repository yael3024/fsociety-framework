"""Typer command line interface."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from fsociety import __version__
from fsociety.core.config import Settings
from fsociety.core.logger import configure_logging
from fsociety.core.permissions import ScopeError
from fsociety.core.platform import platform_info
from fsociety.modules import awareness, forensics, integrity, network, password, system, usb
from fsociety.utils.reports import write_report
from fsociety.utils.terminal import banner, console

app = typer.Typer(no_args_is_help=False, help="FSOCIETY Framework: utilidades defensivas locales.", invoke_without_command=True)
network_app = typer.Typer(help="Inventario seguro de red privada autorizada.")
password_app = typer.Typer(help="Auditoría local de fortaleza de contraseñas.")
integrity_app = typer.Typer(help="Líneas base y verificación de integridad.")
app.add_typer(network_app, name="network")
app.add_typer(password_app, name="password")
app.add_typer(integrity_app, name="integrity")


def settings() -> Settings:
    current = Settings.load()
    current.initialize()
    configure_logging(current.data_dir, current.log_level)
    return current


def show_json(value: object) -> None:
    console.print_json(json.dumps(value, ensure_ascii=False, default=str))


def report(value: dict, prefix: str, cfg: Settings) -> None:
    path = write_report(value, cfg.data_dir, prefix)
    console.print(f"[green]Reporte guardado:[/green] {path}")


@app.callback()
def main(ctx: typer.Context, version: Optional[bool] = typer.Option(None, "--version", "-V", help="Mostrar versión.")) -> None:
    """Lanza el menú cuando no se proporciona un subcomando."""
    if version:
        console.print(f"FSOCIETY Framework {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        settings()
        interactive_menu()


@app.command()
def info() -> None:
    """Mostrar información del sistema y recursos locales."""
    cfg = settings()
    result = {"framework_version": __version__, **platform_info(), **system.system_info()}
    show_json(result)
    report(result, "system_info", cfg)


@app.command()
def processes() -> None:
    """Listar procesos visibles localmente."""
    cfg = settings()
    rows = system.process_inventory()
    table = Table("PID", "Proceso", "Usuario", "Estado", "RAM RSS")
    for item in rows:
        table.add_row(str(item.get("pid", "")), str(item.get("name", "")), str(item.get("username", "")), str(item.get("status", "")), str(item.get("memory_rss", "")))
    console.print(table)
    report({"processes": rows}, "processes", cfg)


@app.command()
def connections() -> None:
    """Listar conexiones locales visibles."""
    cfg = settings()
    rows = system.connection_inventory()
    table = Table("Local", "Remoto", "Estado", "PID")
    for item in rows:
        table.add_row(str(item["local"]), str(item["remote"]), item["status"], str(item["pid"]))
    console.print(table)
    report({"connections": rows}, "connections", cfg)


@network_app.command("scan")
def network_scan(cidr: str = typer.Argument(..., help="CIDR privado, /24 o menor, incluido en config/scope.txt."), yes: bool = typer.Option(False, "--yes", "-y", help="Confirmar explícitamente el escaneo."), timeout: float = typer.Option(0.5, min=0.05, max=3.0), ports: Optional[str] = typer.Option(None, help="Puertos TCP separados por coma.")) -> None:
    """Comprobar conectividad TCP de puertos seleccionados en alcance autorizado."""
    cfg = settings()
    if not yes and not typer.confirm(f"¿Confirmas el inventario TCP de {cidr}? Solo redes privadas registradas en scope.", default=False):
        raise typer.Abort()
    try:
        selected = [int(part.strip()) for part in ports.split(",")] if ports else cfg.network_ports
        result = network.scan_network(cidr, cfg.scope_file, selected, timeout)
    except (ValueError, OSError) as exc:
        console.print(f"[red]Escaneo rechazado o fallido:[/red] {exc}")
        raise typer.Exit(2) from exc
    show_json(result)
    report(result, "network_scan", cfg)


@app.command()
def forensic(path: Path = typer.Argument(..., exists=True, readable=True, help="Archivo o directorio para análisis de solo lectura.")) -> None:
    """Calcular hashes y metadatos de evidencia o inventariar un directorio."""
    cfg = settings()
    result = {"files": forensics.inventory_files(path)} if path.is_dir() else {"evidence": forensics.evidence_record(path)}
    show_json(result)
    report(result, "forensic", cfg)


@app.command("usb")
def usb_scan(path: Optional[Path] = typer.Option(None, "--path", help="Ruta de unidad para inventario estático opcional.")) -> None:
    """Inventariar dispositivos USB; opcionalmente revisar una ruta sin modificarla."""
    cfg = settings()
    result = {"devices": usb.usb_inventory()}
    if path:
        result["inspection"] = usb.inspect_usb_path(path, set(cfg.suspicious_extensions))
    show_json(result)
    report(result, "usb", cfg)


@password_app.command("audit")
def password_audit() -> None:
    """Pedir una contraseña sin mostrarla y evaluarla en memoria local."""
    secret = typer.prompt("Contraseña para evaluar (entrada oculta; no se guarda)", hide_input=True, confirmation_prompt=False)
    result = password.audit_password(secret)
    del secret
    show_json(result)


@integrity_app.command("baseline")
def integrity_baseline(root: Path = typer.Argument(..., exists=True, file_okay=False, readable=True), output: Optional[Path] = typer.Option(None, "--output", "-o")) -> None:
    """Crear línea base SHA-256 con rutas relativas al directorio raíz."""
    cfg = settings()
    target = output or (cfg.data_dir / "reports" / "integrity_baseline.json")
    result = integrity.create_baseline(root, target)
    console.print(f"[green]Línea base creada:[/green] {target} ({len(result['files'])} archivos)")


@integrity_app.command("check")
def integrity_check(root: Path = typer.Argument(..., exists=True, file_okay=False, readable=True), baseline: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True)) -> None:
    """Comparar archivos actuales con una línea base JSON."""
    cfg = settings()
    result = integrity.check_integrity(root, baseline)
    show_json(result)
    report(result, "integrity_check", cfg)
    if not result["ok"]:
        raise typer.Exit(1)


@app.command("awareness")
def awareness_quiz(example: bool = typer.Option(False, "--example", help="Mostrar ejemplo de phishing e indicadores estáticos.")) -> None:
    """Ejecutar un cuestionario o revisar un ejemplo educativo sin envío de datos."""
    if example:
        sample = awareness.EXAMPLE_EMAIL
        result = {"example": sample, "detected_indicators": awareness.phishing_indicators(sample["subject"], sample["sender"], sample["body"])}
        show_json(result)
        report(result, "awareness_example", settings())
        return
    answers = []
    for index, question in enumerate(awareness.QUIZ, 1):
        console.print(f"[bold]{index}. {question['question']}[/bold]")
        for number, option in enumerate(question["options"], 1):
            console.print(f"  {number}. {option}")
        answers.append(typer.prompt("Respuesta", type=int) - 1)
    result = awareness.quiz_result(answers)
    show_json(result)
    report(result, "awareness", settings())


def interactive_menu() -> None:
    banner()
    menu = ["NETWORK SCANNER", "SYSTEM MONITOR", "DIGITAL FORENSICS", "USB GUARDIAN", "PASSWORD AUDITOR", "FILE INTEGRITY", "AWARENESS SIMULATOR", "REPORTS", "SETTINGS", "EXIT"]
    while True:
        table = Table(title="Menú principal", border_style="red")
        for index, item in enumerate(menu, 1):
            table.add_row(str(index % 10), item)
        console.print(table)
        choice = typer.prompt("Selecciona una opción", default="0")
        try:
            if choice == "1":
                cidr = typer.prompt("CIDR a revisar")
                network_scan(cidr, yes=typer.confirm("Confirmar escaneo", default=False), timeout=0.5, ports=None)
            elif choice == "2": info()
            elif choice == "3": forensic(Path(typer.prompt("Archivo o directorio")))
            elif choice == "4": usb_scan()
            elif choice == "5": password_audit()
            elif choice == "6":
                root = Path(typer.prompt("Directorio raíz"))
                if typer.confirm("Crear línea base?", default=False): integrity_baseline(root)
            elif choice == "7": awareness_quiz()
            elif choice == "8":
                cfg = settings()
                paths = sorted((cfg.data_dir / "reports").glob("*.json"))
                console.print("\n".join(str(path) for path in paths) if paths else "Sin reportes todavía.")
            elif choice == "9": show_json({"settings": asdict(Settings.load())})
            elif choice in {"0", "10", "q", "Q"}: break
            else: console.print("[yellow]Opción no válida.[/yellow]")
        except (typer.Abort, typer.Exit):
            console.print("[yellow]Operación cancelada o finalizada.[/yellow]")
        except (ValueError, OSError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
    console.print("[dim]Sesión finalizada.[/dim]")


if __name__ == "__main__":
    app()
