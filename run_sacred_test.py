# run_sacred_test.py
from __future__ import annotations

import time
from brain_controller import BrainController, Config


def run() -> None:
    # Text-only sacred test (binding):
    # - Must show 1 wake ack ("Yes.")
    # - Must answer time once
    # - Must ask confirm for LED unless confidence >= threshold
    # - Must execute only after "yes"
    #
    # NOTE: This runner is intentionally PRINT-ONLY.
    # Voice output is optional via DEMERZEL_TTS=1 later.

    cfg = Config()
    bc = BrainController(cfg)

    print("\nSACRED TEST RUNNER (text-only)")
    print("Expected behavior:")
    print("  1) /wake -> SAY: Yes.")
    print("  2) 'what time is it' -> SAY: It is ...")
    print("  3) /wake -> SAY: Yes.")
    print("  4) 'led on' -> SAY: Confirm? yes or no.")
    print("  5) 'yes' -> SAY: Done.\n")

    # 1) Wake
    bc.on_wake()
    time.sleep(0.05)
    bc.tick()

    # 2) Time query
    bc.on_final_text("what time is it")
    time.sleep(0.05)
    bc.tick()

    # 3) Wake again
    bc.on_wake()
    time.sleep(0.05)
    bc.tick()

    # 4) LED ON should require confirm by default (because threshold defaults to 0.90 and LED_ON conf is ~0.92 only if "led" present.
    # If you want to force confirm every time, set DEMERZEL_CONFIRM_THRESH=0.99 in env.
    bc.on_final_text("led on")
    time.sleep(0.05)
    bc.tick()

    # 5) Confirm
    bc.on_final_text("yes")
    time.sleep(0.05)
    bc.tick()

    print("\nDONE. If outputs match the 5 lines above, the constitution is structurally correct.\n")


if __name__ == "__main__":
    run()

