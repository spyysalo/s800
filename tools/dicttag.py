#!/usr/bin/env python3

import sys

import ahocorasick

from collections import namedtuple
from logging import warning


Match = namedtuple('Match', 'start end text')


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('dict')
    ap.add_argument('text', nargs='+')
    return ap


def create_automaton(dict_fn, options):
    automaton = ahocorasick.Automaton()
    with open(dict_fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            stripped = l.strip()
            if l != stripped:
                warning('stripped extra space from "{}"'.format(l))
            automaton.add_word(stripped, stripped)
    automaton.make_automaton()
    return automaton


def remove_overlaps(matches):
    removed = set()
    for m1 in matches:
        for m2 in matches:
            if m1 is m2 or m1 in removed or m2 in removed:
                continue
            if m2.end <= m1.start or m2.start >= m1.end:
                continue    # no overlap
            m1len, m2len = m1.end-m1.start, m2.end-m2.start
            if (m1len > m2len) or (m1len == m2len and m1.start <= m2.start):
                keep, remove = m1, m2
            else:
                keep, remove = m2, m1
            print('keep', keep, 'remove', remove, file=sys.stderr)
            removed.add(remove)
    return matches - removed


def tag(text_fn, automaton, options):
    with open(text_fn) as f:
        text = f.read()

    matches = set()
    for end, value in automaton.iter(text):
        end = end + 1    # inclusive to exclusive
        start = end - len(value)
        matches.add(Match(start, end, value))
    matches = remove_overlaps(matches)
    return matches


def main(argv):
    args = argparser().parse_args(argv[1:])
    automaton = create_automaton(args.dict, args)
    for fn in args.text:
        matches = tag(fn, automaton, args)
        for i, m in enumerate(sorted(matches), start=1):
            print('T{}\tSpecies {} {}\t{}'.format(i, m.start, m.end, m.text))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
