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

python tools/s800toann.py "$DATA" "$TEXTDIR" "$OUTDIR"
