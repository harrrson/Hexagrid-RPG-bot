#!/bin/bash
SCRIPT=$(realpath -s "$0")
echo "$SCRIPT"
DIR=$(dirname -- "$SCRIPT")
echo "${DIR}"
screen -dSm bot -c "$DIR/.screenrc"
screen -S bot -X bash "source '$DIR/venv/bin/activate'&& cd '$DIR' && python Hexagrid_RPG_bot.py"
