#!/bin/bash

set -u
set -e

SODIR="standoff"
OUTDIR="split-standoff"

if [ ! -d "$SODIR" ]; then
    echo "Missing directory $SODIR (run convert_s800.sh first)" >&2
    exit 1
fi

mkdir -p "$OUTDIR"/{train,devel,test}

for s in train devel test; do
    cat split/$s.txt | while read i; do
	cp "$SODIR"/$i.{txt,ann} "$OUTDIR"/$s
    done
done
