#!/bin/bash

# Displays the record in secdef.dat for a given security ID. Example:
# $ ./find_id.sh 13505

grep 48=$1$'\x01' secdef.dat|tr $'\x01' '\n'
