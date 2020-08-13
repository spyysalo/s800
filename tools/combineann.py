#!/usr/bin/env python3

import sys

from itertools import count
from collections import namedtuple


Textbound = namedtuple('Textbound', 'id type start end text')


Normalization = namedtuple('Normalization', 'id type target norm')


def load_annotations(fn, options):
    annotations = []
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip()
            if l.isspace() or not l:
                continue
            elif l.startswith('T'):
                id_, type_span, text = l.split('\t')
                type_, start, end = type_span.split(' ')
                start, end = int(start), int(end)
                annotations.append(Textbound(id_, type_, start, end, text))
            elif l.startswith('N'):
                id_, type_target_norm = l.split('\t')
                type_, target, norm = type_target_norm.split(' ')
                annotations.append(Normalization(id_, type_, target, norm))
            else:
                raise NotImplementedError(l)
    return annotations


def combine_annsets(anns1, anns2):
    # Eliminate overlaps
    removed1, removed2 = set(), set()
    for a1 in anns1:
        if not isinstance(a1, Textbound):
            continue
        for a2 in anns2:
            if not isinstance(a2, Textbound):
                continue
            if a1.id in removed1 or a2.id in removed2:
                continue
            if a2.end <= a1.start or a2.start >= a1.end:
                continue    # no overlap
            a1len, a2len = a1.end-a1.start, a2.end-a2.start
            if (a1len > a2len) or (a1len == a2len and a1.start <= a2.start):
                print('keep', a1, 'remove', a2, file=sys.stderr)
                removed2.add(a2.id)
            else:
                print('keep', a2, 'remove', a1, file=sys.stderr)
                removed1.add(a1.id)

    # Propagate removals
    for a1 in anns1:
        if isinstance(a1, Normalization) and a1.target in removed1:
            removed1.add(a1.id)
    for a2 in anns2:
        if isinstance(a2, Normalization) and a2.target in removed2:
            removed2.add(a2.id)

    # Create ID mapping
    id_map = {}
    reserved = set([a.id for a in anns1])
    def next_free_id(prefix):
        for i in count(1):
            id_ = '{}{}'.format(prefix, i)
            if id_ not in reserved:
                break
        reserved.add(id_)
        return id_
    for a2 in anns2:
        if a2.id in removed2:
            continue
        if a2.id in reserved:
            id_map[a2.id] = next_free_id(a2.id[0])

    # Combine, remapping IDs from anns2.
    combined = []
    for a1 in anns1:
        if a1.id not in removed1:
            combined.append(a1)
    for a2 in anns2:
        if a2.id in removed2:
            continue
        id_ = id_map.get(a2.id, a2.id)
        if isinstance(a2, Textbound):
            combined.append(Textbound(id_, a2.type, a2.start, a2.end, a2.text))
        elif isinstance(a2, Normalization):
            target = id_map.get(a2.target, a2.target)
            combined.append(Normalization(id_, a2.type, target, a2.norm))
        else:
            raise NotImplementedError()
    return combined


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('ann', nargs='+')
    return ap


def main(argv):
    args = argparser().parse_args(argv[1:])
    annsets = []
    for fn in args.ann:
        annsets.append(load_annotations(fn, args))
    combined = annsets[0]
    for annset in annsets[1:]:
        combined = combine_annsets(combined, annset)
    for a in combined:
        if isinstance(a, Textbound):
            print('{}\t{} {} {}\t{}'.format(*a))
        elif isinstance(a, Normalization):
            print('{}\t{} {} {}'.format(*a))
        else:
            raise NotImplementedError()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
