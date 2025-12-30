#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

export DEMERZEL_TTS=1
export DEMERZEL_VOICE="Samantha"
export DEMERZEL_CONFIRM_THRESH=0.99

python3 -u run_voice_clean.BASELINE_OK.py
