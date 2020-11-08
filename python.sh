#!/bin/bash
DIR=$(dirname -- "$(realpath -s "Hexagrid_RPG_bot.py")")
echo "$DIR"
cd "$DIR"
sleep 10 #Wait for lavalink to start
source "$DIR/venv/bin/activate" # input here your virtualenv activation path
python "$DIR/Hexagrid_RPG_bot.py"
