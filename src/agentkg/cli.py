"""Typer CLI. Entry point: `agentkg` (see [project.scripts])."""
from __future__ import annotations

from pathlib import Path

import typer

from . import log
from .backends import make_backend
from .config import Settings
from .pipeline import run, summarize

app = typer.Typer(help="Biomedical Agent Knowledge Graph pipeline (SPEC.md).",
                  no_args_is_help=True)


def _settings(backend: str | None, list_path: Path | None, out: Path | None) -> Settings:
    """Load .env/env settings, then apply CLI overrides where given."""
    s = Settings()
    if backend:
        s.backend = backend
    if list_path:
        s.list_path = list_path
    if out:
        s.out_path = out
    return s


@app.command(name="run")
def run_pipeline(
    backend: str = typer.Option(None, "--backend", "-b", help="mock | vertex"),
    list_path: Path = typer.Option(None, "--list", "-l", help="awesome-list markdown"),
    out: Path = typer.Option(None, "--out", "-o", help="graph.json output path"),
    limit: int = typer.Option(None, "--limit", "-n", help="process only first N agents"),
    profiles: int = typer.Option(0, "--profiles", "-p", help="draft prose for first N agents"),
    use_sources: bool = typer.Option(False, "--sources", help="crawl SPEC §11 lists instead of list.md"),
    log_level: str = typer.Option(None, "--log-level", help="DEBUG | INFO | WARNING | ERROR"),
):
    """Crawl the list, build the graph, write graph.json."""
    s = _settings(backend, list_path, out)
    log.configure(log_level or s.log_level)
    b = make_backend(s)
    g, review, written = run(s, b, limit=limit, n_profiles=profiles, use_sources=use_sources)
    summary = summarize(g)
    typer.secho(f"backend={b.name}  ->  {s.out_path}", fg=typer.colors.GREEN)
    typer.echo(f"nodes: {summary['nodes']}")
    typer.echo(f"edges: {summary['edges']}")
    typer.echo(f"review log entries: {len(review)} -> {s.review_path}")
    if written:
        typer.echo(f"profiles written: {len(written)} -> {', '.join(written)}")


@app.command()
def config():
    """Print resolved settings (no secrets — auth is via ADC)."""
    s = Settings()
    for k, v in s.model_dump().items():
        typer.echo(f"{k} = {v}")


def main():
    app()


if __name__ == "__main__":
    main()
