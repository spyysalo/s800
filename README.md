# S800 corpus tools

Tools for working with the S800 corpus (http://species.jensenlab.org/).

## Quickstart

    wget http://species.jensenlab.org/files/S800-1.0.tar.gz
    mkdir original-data
    tar xzf S800-1.0.tar.gz -C original-data
    ./convert_s800.sh original-data standoff
    ./split_s800.sh
