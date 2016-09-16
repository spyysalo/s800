import re

from os import path

from collections import OrderedDict
from itertools import chain

ANN_LINE_RE = re.compile(r'^(\d+)\t(\S+):(\S+)\t(\d+)\t(\d+)\t(.+)$')

class FormatError(Exception):
    pass

class Annotation(object):
    def __init__(self, docid, PMID, start, end, norm, text):
        self.docid = docid
        self.PMID = PMID
        self.start = start
        self.end = end
        self.norm = norm
        self.text = text

    def verify(self, text):
        if text[self.start:self.end] != self.text:
            raise FormatError('text mismatch: ann "{}", doc "{}"'.format(
                self.text, text[self.start:self.end]))

    def to_standoff(self, idx):
        return [
            'T{}\tSpecies {} {}\t{}'.format(idx, self.start, self.end,
                                            self.text),
            'N{}\tReference T{} Taxonomy:{}'.format(idx, idx, self.norm)
        ]
        
class Document(object):
    def __init__(self, docid, PMID, text, annotations=None):
        if annotations is None:
            annotations = []
        self.docid = docid
        self.PMID = PMID
        self.text = text
        self.annotations = []

    def add_annotation(self, ann):
        ann.verify(self.text)
        self.annotations.append(ann)

    def to_standoff(self):
        lines = []
        for i, a in enumerate(self.annotations, start=1):
            lines.extend(a.to_standoff(i))
        return lines

def load_document(textdir, docid, PMID):
    fn = path.join(textdir, docid+'.txt')
    with open(fn) as f:
        text = f.read()
    return Document(docid, PMID, text)

def read_s800(flo, textdir):
    """Read S800 corpus annotations from file-like object and annotated
    texts from given directory.

    Each annotation line has the format

         SID <TAB> DOCID:PMID <TAB> START END <TAB> TEXT

    Where SID is the NCBI Taxonomy species ID, DOCID is the S800
    document ID, PMID the document PubMed ID, START and END annotation
    offsets in the text, and TEXT the annotated text.
    """
    document_by_id = OrderedDict()
    for ln, line in enumerate(flo, start=1):
        line = line.rstrip('\n')
        m = ANN_LINE_RE.match(line)
        if not m:
            raise FormatError('Failed to parse line {}: {}'.format(ln, line))
        sid, docid, PMID, start, end, text = m.groups()
        try:
            start = int(start)
            end = int(end) + 1    # S800 uses end-inclusive offsets
        except ValueError:
            raise FormatError('Failed to parse line {}: {}'.format(ln, line))
        ann = Annotation(docid, PMID, start, end, sid, text)
        if docid not in document_by_id:
            document_by_id[docid] = load_document(textdir, docid, PMID)
        doc = document_by_id[docid]
        doc.add_annotation(ann)
    return document_by_id.values()

def load_s800(annfile, textdir):
    with open(annfile) as f:
        return read_s800(f, textdir)
