#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Voice/TTS
export DEMERZEL_TTS=1
export DEMERZEL_VOICE="Samantha"

# Recognition / routing thresholds
export DEMERZEL_CONFIRM_THRESH=0.99

# Make the system stay "in conversation" longer after wake
export DEMERZEL_COMMAND_WINDOW=30.0

# Give you plenty of time to answer yes/no
export DEMERZEL_CONFIRM_WINDOW=20.0

# CRITICAL: stop suppressing yes/no right after wake
# (This is what causes "it won't confirm" and "yes gets ignored".)
export DEMERZEL_IGNORE_YESNO_AFTER_WAKE=0.0
export DEMERZEL_NO_CLARIFY_AFTER_WAKE=0.0

python3 -u run_voice_clean.BASELINE_OK.py
