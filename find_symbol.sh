#!/bin/bash

# Displays the record in secdef.dat for a given symbol. Example:
# $ ./find_symbol.sh ESM3

grep 48=$1$'\x01' secdef.dat|tr $'\x01' '\n'
