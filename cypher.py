#!/usr/bin/env python3
from collections import Counter
from math import ceil, floor
import re
import readline
from shutil import get_terminal_size
import string
from typing import Any

import click

LETTERS = [
    "E",
    "T",
    "A",
    "O",
    "I",
    "N",
    "S",
    "H",
    "R",
    "D",
    "L",
    "C",
    "U",
    "M",
    "W",
    "F",
    "G",
    "Y",
    "P",
    "B",
    "V",
    "K",
    "J",
    "X",
    "Q",
    "Z",
]


class Solver:
    def __init__(self, enciphered: str):
        self.enciphered = enciphered
        """The enciphered string to solve."""
        self.enigma = self.decompose(enciphered)
        """The enciphered string as a list of characters."""
        self.counter = Counter()
        """Counts of letters in the enciphered string."""
        self.decipher: dict[str, str] = dict()
        """Mapping from enciphered letters to plain letters."""
        self.initialize()

    @staticmethod
    def decompose(enciphered: str) -> list[str]:
        """Splits enciphered string into constituent characters."""
        return list(enciphered)

    @property
    def encipher(self) -> dict[str, str]:
        """Uppercase-only mapping of plain letters to enciphered
        letters."""
        return {v: k for k, v in self.decipher.items() if re.match(r"[A-Z]", v)}

    @property
    def choices(self) -> list[str]:
        """List of unique letters in the enciphered string, ordered by
        frequency."""
        return [v for v, __ in self.counter.most_common()]

    @property
    def cipher_chars(self) -> list[str]:
        """List of unique letters in the enciphered string, ordered
        alphanumerically."""
        return sorted([v for v in self.counter.keys()])

    @property
    def unsolved(self) -> list[str]:
        """List of unique letters in the enciphered string that have
        not yet been solved, ordered by frequency."""
        return [
            v for v, count in self.counter.most_common() if self.decipher.get(v) == "_"
        ]

    @property
    def unmapped(self) -> list[str]:
        """List of unique letters that do not yet appear in the
        deciphered string, ordered by frequency of use in English."""
        found = self.encipher.keys()
        return [v for v in LETTERS if v not in found]

    @property
    def is_complete(self) -> bool:
        for v in self.decipher.values():
            if v == "_":
                return False
        return True

    def initialize(self):
        """Count frequencies and prepare decipher mapping."""
        chars = list()
        for char in self.enigma:
            if char in string.ascii_letters:
                self.decipher[char.upper()] = "_"
                self.decipher[char.lower()] = "_"
                chars.append(char.upper())
        self.counter.update(chars)

    def show(self):
        """Print out original enciphered text and solution so far."""
        click.echo("".join(self.enigma))
        solution = [self.decipher.get(v, v) for v in self.enigma]
        click.echo("".join(solution))

    def guess(self, char_from: str, char_to: str):
        """Apply guess, ensuring one-to-one mapping."""
        char_to_uc = char_to.upper()
        if k := self.encipher.get(char_to_uc):
            click.echo(f"You previously thought {k} was {char_to_uc}.")
            self.decipher[k] = "_"
            self.decipher[k.lower()] = "_"
        self.decipher[char_from.upper()] = char_to_uc
        self.decipher[char_from.lower()] = char_to.lower()

    def validate_guess(self, value: str) -> str:
        """If guess is not a single letter or underscore, show solution
        letters that have not yet been picked."""
        if re.match(r"^[_A-Za-z]$", value):
            return value
        else:
            raise click.BadParameter(f"Choose from {', '.join(self.unmapped)}.")

    def solution(self):
        """Print out the finished mapping from enciphered to deciphered
        characters.
        """
        # Turn mapping into list of strings
        entries: list[str] = list()
        keys = self.cipher_chars
        key_width = max([len(k) for k in keys])
        for k in keys:
            entries.append(f"{k:>{key_width}} = {self.decipher[k]}")

        entry_width = 10
        display_width, __ = get_terminal_size()
        cols = floor(display_width / entry_width)
        rows = ceil(len(entries) / cols)
        msg_rows = ["" for __ in range(0, rows)]
        col = 0
        row = 0
        for entry in entries:
            if col < cols:
                col += 1
            else:
                col = 1
                row += 1
            msg_rows[row] += f"{entry:<{entry_width}}"

        for msg in msg_rows:
            click.echo(msg)


class SolverNum(Solver):
    @staticmethod
    def decompose(enciphered: str) -> list[str]:
        """Splits enciphered string into constituent characters."""
        chars = re.split(r"(\D+)", enciphered)
        if not chars[0]:
            chars.pop(0)
        if not chars[-1]:
            chars.pop()
        return chars

    @property
    def cipher_chars(self) -> list[str]:
        """List of unique letters in the enciphered string, ordered
        alphanumerically."""
        return sorted([v for v in self.counter.keys()], key=lambda v: int(v))

    def initialize(self):
        """Counts frequencies and prepares mapping. Looks for
        separated integers instead of letters in the enigma.
        """
        chars = list()
        for char in self.enigma:
            if char.isnumeric():
                self.decipher[char] = "_"
                chars.append(char)
        self.counter.update(chars)

    def guess(self, char_from: str, char_to: str):
        """Apply guess, ensuring one-to-one mapping."""
        char_to_uc = char_to.upper()
        if k := self.encipher.get(char_to_uc):
            click.echo(f"You previously thought {k} was {char_to_uc}.")
            self.decipher[k] = "_"
            self.decipher[k.lower()] = "_"
        self.decipher[char_from] = char_to_uc

    def show(self):
        """Print out original enciphered text and solution so far."""
        click.echo("".join(self.enigma))
        solution = list()
        for se in self.enigma:
            sd = self.decipher.get(se, se)
            wd = len(se)
            sd = f"{sd:>{wd}}"
            solution.append(sd)
        click.echo("".join(solution))


@click.command()
@click.option(
    "-n/-a",
    "--numeric/--alphabetic",
    help="Numeric or alphabetic mode (default = alphabetic)",
)
def main(numeric: bool):
    """Provides an environment for solving substitution ciphers."""
    click.secho("Deciphering Tool\n", fg="blue", bold="True")
    click.secho(
        "Tip: Give a blank guess to see letters you haven't guessed yet.\n",
        fg="green",
    )

    enigma = click.prompt("Enter the ciphered phrase")
    solver = SolverNum(enigma) if numeric else Solver(enigma)

    while True:
        click.echo()
        solver.show()

        if solver.is_complete:
            if click.prompt("\nHappy with that?", type=bool):
                break

        click.echo()
        unsolved = solver.unsolved
        hint = f" [{', '.join(unsolved)}]" if unsolved else ""
        kwargs: dict[str, Any] = dict(default=unsolved[0]) if unsolved else dict()
        char_type = "number" if numeric else "letter"
        char_from = click.prompt(
            f"Pick a {char_type} to decipher{hint}",
            type=click.Choice(solver.choices, case_sensitive=False),
            show_choices=False,
            **kwargs,
        )
        char_to = click.prompt(
            f"What do you think {char_from} is",
            default="?",
            show_default=False,
            prompt_suffix="? ",
            value_proc=solver.validate_guess,
        )
        solver.guess(char_from, char_to)

    click.echo("\nCongratulations!\n")
    solver.solution()


if __name__ == "__main__":
    main()
