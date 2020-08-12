#!/usr/bin/env python

import sys
import re


def text_file_name(annfn):
    return(annfn.replace('.ann', '.txt'))


def norm_space(text):
    start_space = ' ' if re.match(r'^\s.*', text) else ''
    end_space = ' ' if re.match(r'.*\s$', text) else ''
    return start_space + ' '.join(text.split()) + end_space


def get_contexts(annfn, width=30):
    with open(text_file_name(annfn)) as f:
        document = f.read()
    with open(annfn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            if l.isspace() or not l:
                continue
            if l[0] != 'T':
                continue
            fields = l.split('\t')
            id_, type_and_span, text = fields
            type_, start, end = type_and_span.split(' ')
            start, end = int(start), int(end)
            if document[start:end] != text:
                raise ValueError('"{}" vs "{}"'.format(
                    document[start:end], text))
            before = norm_space(document[start-width:start])
            after = norm_space(document[end:end+width])
            print('{}\t{}\t{}<<<{}>>>{}'.format(
                annfn, type_, before, text, after))
            

def main(argv):
    for fn in argv[1:]:
        get_contexts(fn)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
