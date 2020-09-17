#!/bin/bash

set -u
set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 INDIR OUTDIR" >&2
    exit 1
fi

S800DIR="$1"
OUTDIR="$2"

DATA="$S800DIR"/S800.tsv
TEXTDIR="$S800DIR"/abstracts

if [ ! -e "$DATA" ]; then
    echo "Missing data file $DATA" >&2
    exit 1
fi

if [ ! -d "$TEXTDIR" ]; then
    echo "Missing text directory $TEXTDIR" >&2
    exit 1
fi

mkdir -p "$OUTDIR"

# Initialize to empty
cut -f 1,2 "$S800DIR"/pubmedid.tsv | perl -pe 's/PMID://' \
    | while read s i; do
    cp "$S800DIR"/abstracts/$s.txt "$OUTDIR"/$i.txt
    touch "$OUTDIR"/$i.ann
done

# Convert files with annotations
python tools/s800toann.py "$DATA" "$TEXTDIR" "$OUTDIR"
