#!/usr/bin/env python3
from collections import defaultdict
from itertools import combinations

import click


@click.command()
@click.option(
    "-n",
    "--number",
    help="Number of digits (2-7).",
    type=click.IntRange(min=2, max=8),
    default=2,
)
def main(number: int):
    """Shows the possible ways of achieving a given total by summing a
    given number of integers between 1 and 9 inclusive."""

    combos = combinations(range(1, 10), number)
    results = defaultdict(list)
    for combo in combos:
        results[sum(combo)].append(combo)

    for s in sorted(results.keys()):
        click.echo(f"{s:>2}: {', '.join([str(i) for i in results[s]])}")


if __name__ == "__main__":
    main()
