#!/usr/bin/env python3
from collections import Counter
import re
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
    def __init__(self, enigma: str):
        self.enigma = list(enigma)
        """The enciphered string to solve."""
        self.counter = Counter()
        """Counts of letters in the enciphered string."""
        self.decipher: dict[str, str] = dict()
        """Mapping from enciphered letters to plain letters."""
        for char in self.enigma:
            if char in string.ascii_letters:
                self.decipher[char.upper()] = "_"
                self.decipher[char.lower()] = "_"
                self.counter.update(char.upper())

    @property
    def encipher(self) -> dict[str, str]:
        """Uppercase-only mapping of plain letters to enciphered
        letters."""
        return {v: k for k, v in self.decipher.items() if re.match(r"[A-Z]", v)}

    @property
    def choices(self) -> list[str]:
        """List of unique letters in the enciphered string, ordered by
        frequency."""
        return [v for v, count in self.counter.most_common()]

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

    def show(self):
        """Print out original enciphered text and solution so far."""
        click.echo("".join(self.enigma))
        solution = [self.decipher.get(v, v) for v in self.enigma]
        click.echo("".join(solution))

    def guess(self, char_from: str, char_to: str):
        """Apply guess, ensuring one-to-one mapping."""
        if k := self.encipher.get(char_to.upper()):
            click.echo(f"You previously thought that was {k}.")
            self.decipher[k] = "_"
            self.decipher[k.lower()] = "_"
        self.decipher[char_from.upper()] = char_to.upper()
        self.decipher[char_from.lower()] = char_to.lower()

    def validate_guess(self, value: str) -> str:
        if re.match(r"^[_A-Za-z]$", value):
            return value
        else:
            raise click.BadParameter(f"Choose from {', '.join(self.unmapped)}.")


@click.command()
def main():
    """Provides an environment for solving substitution ciphers."""
    enigma = click.prompt("Enter the ciphered phrase")
    solver = Solver(enigma)

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
        char_from = click.prompt(
            f"Pick a letter to decipher{hint}",
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

    click.echo("\nCongratulations!")


if __name__ == "__main__":
    main()
