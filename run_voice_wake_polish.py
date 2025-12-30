#!/usr/bin/env python3

"""
Wake-polish runner for Demerzel.
Does NOT modify baseline files.
"""

from run_voice_clean import main as run_clean

if __name__ == "__main__":
    print("[WAKE_POLISH] Starting wake-polished voice loop")
    run_clean()
