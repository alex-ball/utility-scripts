#! /usr/bin/env python3

import sys
import re
import argparse


def to_binary(n: int, discs: int):
    return bin(n).lstrip('0b').zfill(discs)


def move(n: int, discs: int):
    s = to_binary(n, discs)
    source = (n & n - 1) % 3
    sink = ((n | n - 1) + 1) % 3
    s += f": Move disc from peg {source + 1} to peg {sink + 1}. "
    return s


def print_state(state, with_intro=False):
    pegs = {0: [], 1: [], 2: []}
    discs = len(state)

    # Start peg = 0. Goal peg is:
    goal = 2 if discs % 2 else 1
    half_state = 1 if state[0:1] == '0' else 0
    parity = 0

    # Find biggest disc:
    current_peg = 0 if state[0:1] == '0' else goal
    if with_intro:
        print("\nI'm assuming you have 3 pegs, and you are moving the discs from"
              f" peg 1 to peg {goal}.")
    print(f"\nThe biggest disc is on peg {current_peg + 1}.")
    pegs[current_peg].append(0)
    last_peg = current_peg

    # Find other discs
    d = 1
    while d < discs:
        if state[d - 1:d] == state[d:d + 1]:
            current_peg = last_peg
            parity += 1
        else:
            n = parity + half_state + discs
            if n % 2:
                current_peg = (last_peg - 1) % 3
            else:
                current_peg = (last_peg + 1) % 3

        print(f"The next smallest disc is on peg {current_peg + 1}.")
        pegs[current_peg].append(d)
        last_peg = current_peg
        d += 1

    pegstr = dict()
    for key, val in pegs.items():
        pegstr[key] = [f"{discs - p}" for p in pegs[key]]

    print(f"\nWith the discs numbered from smallest (1) to largest ({discs}),")
    for n in range(0, 3):
        if len(pegs[n]) > 1:
            print(f"- peg {n + 1} contains discs {', '.join(pegstr[n])}.")
        elif len(pegs[n]):
            print(f"- peg {n + 1} contains disc {', '.join(pegstr[n])}.")
        else:
            print(f"- peg {n + 1} is empty.")
    print()


parser = argparse.ArgumentParser(
    description="Presents a step-by-step solution for the Tower of Hanoi puzzle"
    " in terms of binary numbers. Press return to advance to the next step, or"
    " ‘help’ and return to review where all the discs should be.")
parser.add_argument(
    '-s', '--step',
    help="instead of stepping through a solution, interpret this binary number"
          " (e.g. 101) as a Tower of Hanoi step state.",
    action='store')
args = parser.parse_args()

print("TOWER OF HANOI SOLVER")

state = args.step

if state is None:
    # Step through a solution:
    print("\nI'm assuming you have 3 pegs.")
    discs = None
    while discs is None:
        disc_str = input("How many discs? > ")
        try:
            discs = int(disc_str)
        except:
            print("Please type a whole number.")
            discs = None

    any = input(f"{'0'.zfill(discs)}: All discs should be on peg 1. ")

    n = 1
    last = 2 ** discs
    while n < last:
        any = input(move(n, discs))
        if any.lower() == 'help':
            print_state(to_binary(n, discs))
        n += 1
    print("Finished!")

    sys.exit(0)

if re.search(r'[^01]', state):
    print("Just ones and zeroes, please.")
    sys.exit(0)

print_state(state, with_intro=True)
