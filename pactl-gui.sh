#!/bin/bash

# Launch the PulseAudio Control GUI from its directory
cd "$(dirname "$(readlink -f "$0")")"
python3 src/main.py 
