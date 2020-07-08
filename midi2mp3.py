#!/usr/bin/env python3

import os
import sys
import argparse
from tempfile import NamedTemporaryFile
import subprocess
from time import strftime
import mido


def concat_midi(args, outfile):
    """Creates the midi outfile by concatenating the list of midi infiles in the
    order specified. Returns true on success and false on failure."""

    # Lilypond uses 384 ticks per beat.
    tpb = 384

    # Set up new midi file
    outmidifile = mido.MidiFile(type=1, ticks_per_beat=tpb)
    end_of_track = 0
    end_of_lyric = 0

    # Process files
    for f, infile in enumerate(args.midifiles):
        inmidifile = mido.MidiFile(infile)
        end_of_last = end_of_track
        this_length = 0

        # MIDI default tempo is 500000 µs/beat.
        # Code assumes all tempo changes are in the same track.
        tempo = 500000

        for i, intrack in enumerate(inmidifile.tracks):
            needs_padding = False
            #  Identify a track to add the messages to.
            outtrack = mido.MidiTrack()
            if len(outmidifile.tracks) < (i + 1):
                outmidifile.tracks.append(outtrack)
                if f and i:
                    needs_padding = True
            else:
                outtrack = outmidifile.tracks[i]

            is_lyrics = False
            # Get the messages and add to corresponding track:
            for msg in intrack:
                if needs_padding and msg.type == 'note_on':
                    needs_padding = False
                    outtrack.append(
                        mido.MetaMessage('marker', text='', time=end_of_last))
                    outtrack.append(msg)
                elif msg.type == 'lyrics':
                    is_lyrics = True
                elif msg.type == 'end_of_track':
                    if is_lyrics:
                        end_of_lyric = msg.time
                    elif i == 0:
                        this_length = msg.time
                        end_of_track += msg.time
                elif msg.type == "set_tempo":
                    tempo = msg.tempo
                    outtrack.append(msg)
                else:
                    outtrack.append(msg)

            # Add inter-file gap
            delta = round(mido.second2tick(args.gap, tpb, tempo))
            if (f + 1) == len(args.midifiles):
                # Last file so use tail time instead
                delta = round(mido.second2tick(args.tail, tpb, tempo))
            if i == 0:
                end_of_track += delta
                this_length += delta
            elif is_lyrics:
                outtrack.append(
                    mido.MetaMessage(
                        'marker', text='', time=end_of_lyric + delta))
            else:
                outtrack.append(mido.MetaMessage('marker', text='', time=delta))

        # Pad any unaltered tracks to the right length
        for i, outtrack in enumerate(outmidifile.tracks):
            if i < len(inmidifile.tracks):
                continue
            outtrack.append(
                mido.MetaMessage('marker', text='', time=this_length))

    # Tail files with end of track markers
    for i, outtrack in enumerate(outmidifile.tracks):
        if i == 0:
            outtrack.append(
                mido.MetaMessage('end_of_track', time=end_of_track))
        else:
            outtrack.append(
                mido.MetaMessage('end_of_track', time=0))

    # Save new midi file
    if len(outmidifile.tracks):
        outmidifile.save(outfile)
        return True

    return False


def do_sequential_conversion(args):
    with NamedTemporaryFile(suffix='.midi') as f:
        print("Preparing MIDI for conversion...")
        concat_midi(args, f.name)
        if not os.path.isfile(f.name):
            print("Failed to generate intermediate MIDI file.")
            sys.exit(1)

        print("Converting MIDI to raw audio...")
        try:
            wav = subprocess.run(
                f"fluidsynth -l -T raw -F - '{args.soundfont}' '{f.name}'",
                shell=True, check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print("Failed to convert MIDI to raw audio.")
            print(e)
            sys.exit(1)

        print("Encoding audio as MP3...")
        try:
            subprocess.run(
                f"lame -b 256 -r - '{args.out}'",
                shell=True, check=True, input=wav.stdout)
        except subprocess.CalledProcessError as e:
            print("Failed to convert WAV to MP3.")
            print(e)
            sys.exit(1)


def do_streamed_conversion(args):
    with NamedTemporaryFile(suffix='.midi') as f:
        print("Preparing MIDI for conversion...")
        concat_midi(args, f.name)
        if not os.path.isfile(f.name):
            print("Failed to generate intermediate MIDI file.")
            sys.exit(1)

        print("Converting MIDI to MP3...")
        wav = subprocess.Popen(
            f"fluidsynth -l -T raw -F - '{args.soundfont}' '{f.name}'",
            shell=True,
            stdout=subprocess.PIPE)

        mp3 = subprocess.Popen(
            f"lame -b 256 -r - '{args.out}'",
            shell=True,
            stdin=wav.stdout)

        wav_rc = wav.wait()
        if wav_rc != 0:
            print("Failed to convert MIDI to WAV"
                  f" (fluidsynth exit status {wav_rc}).")
            sys.exit(1)
        mp3_rc = mp3.wait()
        if mp3_rc != 0:
            print("Failed to convert WAV to MP3"
                  f" (lame exit status {mp3_rc}).")
            sys.exit(1)


def main():
    """Converts MIDI to MP3."""
    parser = argparse.ArgumentParser(
        description="Converts one or more MIDI files to a single MP3.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-g', '--gap',
        help="seconds to insert between input tracks",
        type=float,
        default=2.0)
    parser.add_argument(
        '-t', '--tail',
        help="seconds of silence to append",
        type=float,
        default=1.0)
    parser.add_argument(
        '-o', '--out',
        help="output filename, if it should differ from first input apart from"
             " extension",
        type=str)
    parser.add_argument(
        '-p', '--parallel',
        help="generate audio and encode to MP3 in parallel instead of"
             " sequentially",
        action='store_true')
    parser.add_argument(
        '-s', '--soundfont',
        help="path to soundfont to use",
        metavar='SF2',
        type=str,
        default='/usr/share/sounds/sf2/FluidR3_GM.sf2')
    parser.add_argument(
        'midifiles',
        help="MIDI file",
        metavar='MID',
        nargs='+')

    args = parser.parse_args()

    # Check files exist
    has_badfile = False
    for midifile in args.midifiles:
        if not os.path.isfile(midifile):
            print(f"Cannot find file {midifile}.")
            has_badfile = True

    if not os.path.isfile(args.soundfont):
        print(f"Cannot find soundfont {args.soundfont}.")
        has_badfile = True

    if has_badfile:
        print("Please check before continuing.")
        sys.exit(1)

    # Set fallback output filename
    if not args.out:
        first_input = os.path.basename(args.midifiles[0])
        args.out = os.path.splitext(first_input)[0] + ".mp3"

    # Check suitability
    if os.path.isfile(args.out):
        print(f"Action would overwrite existing file {args.out}.")
        answer = input("Continue? (y/N) > ")
        if not answer.lower().startswith('y'):
            print("Please re-run, selecting a new output file name with the"
                  " --out option.")
            sys.exit(0)

    # Run operations
    if args.parallel:
        do_streamed_conversion(args)
    else:
        do_sequential_conversion(args)

    # Finish
    print(f"MP3 file {args.out} created successfully.")


if __name__ == "__main__":
    main()
