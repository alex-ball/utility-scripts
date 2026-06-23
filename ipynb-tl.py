#!/usr/bin/env python3
import json
import secrets
from typing import TextIO

import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """Translates between regular scripts and Jupyter notebooks."""

@main.command(short_help="Extracts code from notebook.")
@click.argument(
    "filepath",
    type=click.File(),
)
@click.option(
    "-o",
    "--output",
    type=click.File(mode="w"),
    help="File path for output or '-' for STDOUT (default)",
    default="-",
)
def extract(filepath: TextIO, output: TextIO):
    """Extracts and concatenates the code content from a Jupyter notebook.
    FILEPATH can be the path to a Jupyter notebook file (*.ipynb) or '-' for
    STDIN.
    """
    try:
        nb_content = json.load(filepath)
        assert isinstance(nb_content, dict)
        assert "cells" in nb_content
    except (json.JSONDecodeError, AssertionError):
        raise click.ClickException("Cannot parse input. Aborting.")

    nl_needed = 0
    last_line = ""
    for cell in nb_content["cells"]:
        if (cell.get("cell_type") or "") != "code":
            continue
        lines: list[str] = cell.get("source") or []
        if not lines:
            continue
        for _ in range(nl_needed):
            output.write("\n")
        for line in lines:
            output.write(line)
        last_line = lines[-1]
        if last_line == "\n":
            nl_needed = 0
        else:
            nl_needed = 2

    if not last_line.endswith("\n"):
        output.write("\n")


class Cell:
    def __init__(self, lines: list[str]):
        self.source = lines
        self.id = secrets.token_hex(4)

    def as_dict(self) -> dict:
        return {
            "cell_type": "code",
            "execution_count": None,
            "id": self.id,
            "metadata": {},
            "outputs": [],
            "source": self.source,
        }


@main.command(short_help="Splits code into notebook cells.")
@click.argument(
    "filepath",
    type=click.File(),
)
@click.option(
    "-o",
    "--output",
    type=click.File(mode="w"),
    help="File path for output or '-' for STDOUT (default)",
    default="-",
)
@click.option(
    "-l",
    "--lang",
    help="Language of input script (default 'python')",
    default = "python",
)
def create(filepath: TextIO, output: TextIO, lang: str):
    """Creates a new Jupyter notebook by splitting the input code into cells,
    using double-blank lines as cell boundaries.
    """
    nb = {
        "cells": [],
        "metadata": {"language_info": {"name": lang }},
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    line_buffer = []
    blanks = 0

    for line in filepath:
        if line == "\n":
            blanks += 1
            if blanks == 2:
                line_buffer.pop()
                nb["cells"].append(Cell(line_buffer).as_dict())
                line_buffer = []
            else:
                line_buffer.append(line)
        else:
            blanks = 0
            line_buffer.append(line)

    if line_buffer:
        nb["cells"].append(Cell(line_buffer).as_dict())

    json.dump(nb, output, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
