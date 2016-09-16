#!/usr/bin/env python

from __future__ import print_function

import sys

from os import path

from s800 import load_s800

def main(argv):
    if len(argv) != 4:
        print('Usage: {} ANNFILE TEXTDIR OUTDIR'.format(__file__),
              file=sys.stderr)
        return 1
    annfile, textdir, outdir = argv[1:]

    for d in (textdir, outdir):
        if not path.isdir(d):
            print('Not a directory: {}'.format(d), file=sys.stderr)
            return 1

    documents = load_s800(annfile, textdir)

    for d in documents:
        with(open(path.join(outdir, d.PMID+'.txt'), 'wt')) as out:
            out.write(d.text)
        with(open(path.join(outdir, d.PMID+'.ann'), 'wt')) as out:
            print('\n'.join(d.to_standoff()), file=out)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
