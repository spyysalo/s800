#!/usr/bin/env python3

import sys
import os
import re

from collections import namedtuple, defaultdict
from logging import warning


#  alnum sequences single tokens, rest are single-character tokens.
TOKENIZATION_RE = re.compile(r'([^\W_]+|.)')


Textbound = namedtuple('Textbound', 'id type start end text source')


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('-r', '--remove', default=None, metavar='TYPE[,TYPE[...]]')
    ap.add_argument('ann', nargs='+')
    return ap


def text_file_name(ann_fn):
    return ann_fn.replace('.ann', '.txt')


def read_text(fn):
    with open(fn) as f:
        return f.read()


def remove_nested(anns):
    removed = set()
    for i, a1 in enumerate(anns):
        for j, a2 in enumerate(anns):
            if a1.start > a2.start and a1.end <= a2.end:
                removed.add(i)
            elif a1.start >= a2.start and a1.end < a2.end:
                removed.add(i)
    filtered = []
    for i, a in enumerate(anns):
        if i not in removed:
            filtered.append(a)
    return filtered


def read_anns(fn, source, options):
    anns = []
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            if l.startswith('#'):
                continue
            elif not l.startswith('T'):
                warning(l)
                continue
            fields = l.split('\t')
            id_, type_span, text = fields
            type_, start, end = type_span.split(' ')
            start, end = int(start), int(end)

            if type_ in options.remove:
                continue

            ann = Textbound(id_, type_, start, end, text, source)
            anns.append(ann)
    anns = remove_nested(anns)
    return anns


def read_data(ann_fns, options):
    max_prefix = None
    for ann_fn in ann_fns:
        id_ = os.path.splitext(ann_fn)[0]
        if max_prefix is None:
            max_prefix = id_
        else:
            for i in range(len(max_prefix)):
                if i >= len(id_) or max_prefix[i] != id_[i]:
                    max_prefix = max_prefix[:i]
                    break
    print('prefix:', max_prefix)
    
    ann_map, txt_map = {}, {}
    for ann_fn in ann_fns:
        id_ = os.path.splitext(ann_fn)[0]
        id_ = id_[len(max_prefix):]
        txt_fn = text_file_name(ann_fn)
        txt = read_text(txt_fn)
        anns = read_anns(ann_fn, id_, options)
        assert id_ not in ann_map
        ann_map[id_] = anns
        assert id_ not in txt_map
        txt_map[id_] = txt
    return txt_map, ann_map


def tokenize(text):
    tokens = [t for t in TOKENIZATION_RE.split(text) if t]
    assert ''.join(tokens) == text
    return tokens


def find_expansions(ann, txt, ann_by_text, max_tokens=10):
    before = txt[:ann.start]
    after = txt[ann.end:]
    before_toks = tokenize(before)
    after_toks = tokenize(after)

    for a in range(max_tokens+1):
        if a >= len(after_toks):
            break
        for b in range(max_tokens+1):
            if a == 0 and b == 0:
                continue
            if b >= len(before_toks):
                break
            before_exp = '' if b == 0 else ''.join(before_toks[-b:])
            after_exp = ''.join(after_toks[:a])

            expanded = before_exp + ann.text + after_exp
            if expanded in ann_by_text:
                exp_source = ' '.join([e.source for e in ann_by_text[expanded]])
                print('{}\t->\t{}\t({} -> {})'.format(
                    ann.text, expanded, ann.source, exp_source))


def main(argv):
    args = argparser().parse_args(argv[1:])
    if args.remove is None:
        args.remove = set()
    else:
        args.remove = set(args.remove.split(','))

    txt_map, ann_map = read_data(args.ann, args)

    ann_by_text = defaultdict(list)
    for anns in ann_map.values():
        for a in anns:
            ann_by_text[a.text].append(a)

    for i in ann_map:
        txt, anns = txt_map[i], ann_map[i]
        for a in anns:
            find_expansions(a, txt, ann_by_text)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
