#!/bin/bash
DIR=$(dirname -- "$(realpath -s "Hexagrid_RPG_bot.py")")
echo "$DIR"
cd "$DIR/lavalink"
java -jar Lavalink.jar
