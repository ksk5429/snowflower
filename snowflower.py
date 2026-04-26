"""snowflower content orchestrator (CLI entry point).

Usage:
  python snowflower.py health-check
  python snowflower.py publish --episode ep001_episode.yaml --dry-run
  python snowflower.py publish --episode ep001_episode.yaml --live --platforms youtube,linkedin,bluesky
  python snowflower.py list-platforms
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows codepages so Rich tables don't crash on
# en-dashes, em-dashes, or Korean characters.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

import typer
import yaml
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from connectors_registry import REGISTRY, get_connector
from models import Episode, PublishResult


app = typer.Typer(help="snowflower content engine")
console = Console()


def _load_episode(yaml_path: Path) -> Episode:
    if not yaml_path.exists():
        raise FileNotFoundError(f"Episode YAML not found: {yaml_path}")
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    base_dir = yaml_path.parent

    def _resolve(p: str | None) -> Path | None:
        if not p:
            return None
        return (base_dir / p).resolve()

    return Episode(
        id=data["id"],
        title=data["title"],
        description=data.get("description", ""),
        tags=data.get("tags", []),
        video_path=_resolve(data.get("video_path")),
        audio_path=_resolve(data.get("audio_path")),
        image_paths=[Path(_resolve(p)) for p in data.get("image_paths", []) if p],  # type: ignore[arg-type]
        long_form_text=data.get("long_form_text"),
        short_text=data.get("short_text"),
        disclosure_kind=data.get("disclosure_kind", "neutral"),
        disclosure_text=data.get("disclosure_text", ""),
        target_languages=data.get("target_languages", ["en"]),
    )


def _render_health(rows: list[dict]) -> None:
    table = Table(title="snowflower connector health")
    table.add_column("platform", style="cyan")
    table.add_column("ready", style="green")
    table.add_column("oauth")
    table.add_column("app review")
    table.add_column("manual only")
    table.add_column("notes", overflow="fold")
    for r in rows:
        table.add_row(
            r["name"],
            "OK" if r["ready"] else "no",
            "yes" if r["requires_oauth"] else "no",
            "yes" if r["requires_app_review"] else "no",
            "yes" if r.get("manual_only") else "no",
            r.get("notes", ""),
        )
    console.print(table)


def _render_results(results: list[PublishResult]) -> None:
    table = Table(title="snowflower publish results")
    table.add_column("platform", style="cyan")
    table.add_column("status", style="bold")
    table.add_column("url / id", overflow="fold")
    table.add_column("cost $", justify="right")
    table.add_column("note", overflow="fold")
    for r in results:
        style = {
            "published": "green",
            "queued": "yellow",
            "dry_run": "blue",
            "blocked_app_review": "yellow",
            "blocked_manual_only": "yellow",
            "blocked_no_credentials": "yellow",
            "error": "red",
            "not_implemented": "magenta",
        }.get(r.status, "")
        table.add_row(
            r.platform,
            f"[{style}]{r.status}[/{style}]" if style else r.status,
            r.url or r.post_id or "",
            f"{r.cost_usd:.3f}",
            r.error or r.note or "",
        )
    console.print(table)


@app.command()
def health_check() -> None:
    """Probe every registered connector for credentials + readiness."""
    load_dotenv()
    rows = [get_connector(name).health_check() for name in REGISTRY]
    _render_health(rows)


@app.command()
def publish(
    episode: Path = typer.Option(..., "--episode", "-e", help="Path to episode YAML"),
    platforms: str = typer.Option(
        "all", "--platforms", "-p", help="Comma list or 'all'"
    ),
    dry_run: bool = typer.Option(True, "--dry-run/--live", help="Default dry-run"),
) -> None:
    """Adapt episode -> per-platform Post -> publish (or dry-run)."""
    load_dotenv()
    ep = _load_episode(episode)
    selected = list(REGISTRY) if platforms == "all" else [p.strip() for p in platforms.split(",")]

    if not dry_run:
        console.print("[bold red]LIVE MODE: real API calls will be made[/bold red]")

    results: list[PublishResult] = []
    for name in selected:
        if name not in REGISTRY:
            console.print(f"[yellow]skip unknown platform: {name}[/yellow]")
            continue
        connector = get_connector(name)
        post = connector.adapt(ep)
        results.append(connector.publish(post, dry_run=dry_run))

    _render_results(results)

    out_path = episode.parent / f"{ep.id}_results.json"
    out_path.write_text(
        json.dumps([r.model_dump(mode="json") for r in results], indent=2, default=str),
        encoding="utf-8",
    )
    console.print(f"[dim]results saved to {out_path}[/dim]")


@app.command()
def list_platforms() -> None:
    """List registered platforms."""
    for name, cls in REGISTRY.items():
        console.print(f"  - [cyan]{name}[/cyan]  {cls.notes}")


if __name__ == "__main__":
    app()
