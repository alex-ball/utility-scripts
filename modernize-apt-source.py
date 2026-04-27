#!/usr/bin/env python3
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple, Self

import click


class Option(NamedTuple):
    old: str
    new: str
    multi: bool


OPTIONS = [
    Option("include", "Include", True),
    Option("exclude", "Exclude", True),
    Option("arch", "Architectures", True),
    Option("lang", "Languages", True),
    Option("target", "Targets", True),
    Option("pdiffs", "PDiffs", False),
    Option("by-hash", "By-Hash", False),
    Option("allow-insecure", "Allow-Insecure", False),
    Option("allow-weak", "Allow-Weak", False),
    Option("allow-downgrade-to-insecure", "Allow-Downgrade-To-Insecure", False),
    Option("trusted", "Trusted", False),
    Option("signed-by", "Signed-By", False),
    Option("check-valid-until", "Check-Valid-Until", False),
    Option("valid-until-min", "Valid-Until-Min", False),
    Option("valid-until-max", "Valid-Until-Max", False),
    Option("check-date", "Check-Date", False),
    Option("inrelease-path", "InRelease-Path", False),
    Option("snapshot", "Snapshot", False),
]


@dataclass
class Deb822:
    """Data structure used by deb822."""

    name: str = ""
    enabled: bool = True
    types: list[str] = field(default_factory=list)
    uris: list[str] = field(default_factory=list)
    suites: list[str] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    options: dict[str, list[str] | str] = field(default_factory=dict)

    def merge_success(self, other: Self) -> bool:
        """Attempts to merge multiple lines."""
        if other.uris != self.uris or other.enabled != self.enabled:
            return False
        for opt in OPTIONS:
            if opt.multi:
                continue
            if other.options.get(opt.new) != self.options.get(opt.new):
                return False
        for v in [v for v in other.types if v not in self.types]:
            self.types.append(v)
        for v in [v for v in other.suites if v not in self.suites]:
            self.types.append(v)
        for v in [v for v in other.components if v not in self.components]:
            self.types.append(v)
        for opt in OPTIONS:
            if not opt.multi:
                continue
            if opt.new not in other.options:
                continue
            if opt.new in self.options:
                other_opts = other.options[opt.new]
                self_opts = self.options[opt.new]
                assert isinstance(other_opts, list)
                assert isinstance(self_opts, list)
                for v in [v for v in other_opts if v not in self_opts]:
                    self_opts.append(v)
            else:
                self.options[opt.new] = other.options[opt.new]
        return True

    def render(self) -> str:
        """Renders self as multiline string."""
        plural_map = {
            "Types": self.types,
            "URIs": self.uris,
            "Suites": self.suites,
            "Components": self.components,
        }
        lines: list[str] = list()
        if self.name:
            lines.append(f"X-Repolib-Name: {self.name}")
        if not self.enabled:
            lines.append("Enabled: no")
        for key, values in plural_map.items():
            if values:
                value = " ".join(values)
                lines.append(f"{key}: {value}")
        for opt in OPTIONS:
            if val := self.options.get(opt.new):
                if isinstance(val, list):
                    lines.append(f"{opt.new}: {' '.join(val)}")
                else:
                    lines.append(f"{opt.new}: {val}")
        return "\n".join(lines) + "\n"


def parse_sl(infile: Path) -> list[Deb822]:
    """Opens and parses a sources.list file."""
    sources: list[Deb822] = list()
    with infile.open() as f:
        for line in f:
            if not line or line == "\n":
                continue
            m = re.match(
                r"(?P<off># *)?"
                + r"(?P<typ>deb(?:-src)?) "
                + r"(?P<opt>\[[^\]]+\] )?"
                + r"(?P<uri>(?:http|file)\S+) "
                + r"(?P<sui>\S+)"
                + r"(?: (?P<com>[^#\n]+)"
                + r"(?P<cmt> #[^\n]*)?)?\n$",
                line,
            )
            if not m:
                if line.startswith("#"):
                    continue
                click.secho(f"Could not parse line:\n{line}", err=True, fg="yellow")
                continue
            source = Deb822(
                types=[m.group("typ")],
                uris=[m.group("uri")],
                suites=[m.group("sui")],
            )
            if components := m.group("com"):
                source.components = components.split()
            if comment := m.group("cmt"):
                source.name = comment.strip(" #")
            if opt_block := m.group("opt"):
                # Strip off delimiters
                opt_inner = opt_block.strip("[ ]")
                # Separate
                opt_args = opt_inner.split()
                for opt_arg in opt_args:
                    err = f"Unrecognized option: {opt_arg}"
                    kvs = opt_arg.strip().split("=", maxsplit=1)
                    if len(kvs) != 2:
                        click.secho(err, err=True, fg="yellow")
                        continue
                    for opt in OPTIONS:
                        if kvs[0] == opt.old:
                            source.options[opt.new] = (
                                kvs[1].split(",") if opt.multi else kvs[1]
                            )
                            break
                    else:
                        click.secho(err, err=True, fg="yellow")
                        continue
            if m.group("off"):
                source.enabled = False
            if (not sources) or (not sources[-1].merge_success(source)):
                sources.append(source)
    return sources


@click.command()
@click.option(
    "-i",
    "--input",
    "infiles",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    multiple=True,
    help="Sources list to convert.",
)
def main(infiles: tuple[Path, ...]):
    """Converts a Debian source list from the old sources.list format
    to the newer, multiline, deb822 format.
    """
    to_do: list[tuple[Path, list[Deb822]]] = list()
    if infiles:
        for infile in infiles:
            err = f"Skipping {infile.name}..."

            if not infile.suffix == ".list":
                click.secho(err, err=True, fg="yellow")
                continue
            sources = parse_sl(infile)

            if not sources:
                click.secho(err, err=True, fg="yellow")
                continue
            to_do.append((infile, sources))
    else:
        cwd = Path.cwd()
        for infile in sorted(cwd.iterdir(), key=lambda v: v.name):
            if not infile.suffix == ".list":
                continue
            sources = parse_sl(infile)
            err = f"Skipping {infile.name}..."

            if not sources:
                click.secho(err, err=True, fg="yellow")
                continue
            to_do.append((infile, sources))

    for infile, sources in to_do:
        outfile = infile.with_suffix(".sources")
        if outfile.is_file():
            click.secho(f"{outfile.name} exists, not replacing.", err=True, fg="yellow")
            continue

        with outfile.open("w") as f:
            converted = "\n\n".join([v.render() for v in sources])
            f.write(converted)


if __name__ == "__main__":
    main()
