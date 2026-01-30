from __future__ import annotations

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


def generate_markdown_report(
    *,
    input_data,
    scores,
    recommendations,
) -> str:
    template = env.get_template("advisory_report.md.j2")
    return template.render(
        input=input_data,
        scores=scores,
        recommendations=recommendations,
    )
