#!/usr/bin/env python

import sys
import re

from argparse import ArgumentParser


# Match prefixes not part of names
PREFIX_RE = re.compile(r'^([Aa]nti\s*-\s*).*')

# Match premodifiers not part of names
PREMODIFIER_RE = re.compile(r'^(([Nn]ative|[Gg]enus)\s+).*')

# Match following type strain marker string "(T)"
TYPE_STRAIN_RE = re.compile(r'^(\s*\(T\)).*')

# Match ending "sp. nov." and similar
SPEC_NOV_RE = re.compile(r'.*?(((\s*gen\.\s*n(ov)?\.|\s*n(ov)?\.\s*gen\.),?)?\s*(sp(ec)?\.\s*n(ov)?\.|n(ov)?\.\s*sp(ec)?\.)\s*)$')

# Match ending common head nouns
COMMON_HEAD_RE = re.compile(r'.+?(\s+(plants?|strains?)\s*)$')


# Regular expressions run against the context after a span and added if matched
ADD_AFTER = [
    TYPE_STRAIN_RE,
]

# Regular expressions run against the span and removed if matched
REMOVE_START = [
    PREFIX_RE,
    PREMODIFIER_RE,
]

# Regular expressions run against the span and removed if matched
REMOVE_END = [
    SPEC_NOV_RE,
    COMMON_HEAD_RE,
]

def argparser():
    ap = ArgumentParser()
    ap.add_argument('ann', nargs='+')
    return ap


def text_file_name(annfn):
    return(annfn.replace('.ann', '.txt'))


def fix_span(document, line):
    fields = line.split('\t')
    id_, type_and_span, text = fields
    type_, start, end = type_and_span.split(' ')
    start, end = int(start), int(end)
    if document[start:end] != text:
        raise ValueError('"{}" vs "{}"'.format(document[start:end], text))
    before = document[:start]
    after = document[end:]

    while True:
        prev_text = text
        for regex in ADD_AFTER:
            m = regex.match(after)
            if m:
                addition = m.group(1)    # add to end of span
                end = end + len(addition)
                text = text + addition
                after = after[len(addition):]
        for regex in REMOVE_START:
            m = regex.match(text)
            if m:
                removal = m.group(1)
                start = start + len(removal)
                text = text[len(removal):]
                before = before + removal
        for regex in REMOVE_END:
            m = regex.match(text)
            if m:
                removal = m.group(1)    # remove from end of span
                end = end - len(removal)
                text = text[:-len(removal)]
                after = removal + after
        if prev_text == text:
            break    # no changes

    return id_, type_, start, end, text
    

def get_contexts(annfn):
    with open(text_file_name(annfn)) as f:
        document = f.read()
    with open(annfn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            if l.isspace() or not l:
                print(l)
            elif l[0] != 'T':
                print(l)
            else:
                fields = fix_span(document, l)
                print('{}\t{} {} {}\t{}'.format(*fields))
                

def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.ann:
        get_contexts(fn)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
