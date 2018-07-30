# S800 corpus tools

Tools for working with the S800 corpus (http://species.jensenlab.org/). Requires `python2`.

## Quickstart

### Convert S800 corpus to standoff format (`.ann`)

```bash
# Clone this repository
$ git clone https://github.com/spyysalo/s800.git

# Go into the repository
$ cd s800

# Collect the S800 corpus
$ wget http://species.jensenlab.org/files/S800-1.0.tar.gz
$ mkdir original-data
$ tar xzf S800-1.0.tar.gz -C original-data

# Convert the S800 corpus into standoff format
$ ./convert_s800.sh original-data standoff
$ ./split_s800.sh
```

### Convert standoff to CoNLL format

```bash
# Make sure the previous steps are complete, and that we are in the s800 repository
$ cd s800
$ mkdir conll

# Clone the standoff2conll tool
$ git clone https://github.com/spyysalo/standoff2conll.git

# Convert s800 corpus from standoff to CoNLL format
$ for i in train devel test; do
    python2 standoff2conll/standoff2conll.py split-standoff/$i > conll/$i.tsv
  done
