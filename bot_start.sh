#!/bin/bash
SCRIPT=$(realpath -s "$0")
echo "$SCRIPT"
DIR=$(dirname -- "$SCRIPT")
echo "${DIR}"
screen -dSm bot -c "$DIR/.screenrc"