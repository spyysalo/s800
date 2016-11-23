# S800 corpus tools

Tools for working with the S800 corpus (http://species.jensenlab.org/).

## Quickstart: conversion to `.ann` standoff

    wget http://species.jensenlab.org/files/S800-1.0.tar.gz
    mkdir original-data
    tar xzf S800-1.0.tar.gz -C original-data
    ./convert_s800.sh original-data standoff
    ./split_s800.sh

## Convert standoff to CoNLL format

    mkdir conll
    git clone git@github.com:spyysalo/standoff2conll.git
    for i in train devel test; do
        python standoff2conll/standoff2conll.py split-standoff/$i > conll/$i.tsv
    done
