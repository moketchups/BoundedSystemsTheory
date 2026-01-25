#!/bin/bash
# demerzel_run.sh - EXACT COPY, NO MODIFICATIONS

echo "Starting Demerzel v2.0"
echo "Step 1: Hardware connection"
scp moketchups@192.168.0.161:~/sensor_data.csv ./sensor_data.csv
echo "Step 1 complete"

echo "Step 2: Pattern detection"
echo "Step 3: Output with awareness tags"
python3 pattern_detect.py
echo "Step 2 complete"
echo "Step 3 complete"

echo "System complete. No further action."
