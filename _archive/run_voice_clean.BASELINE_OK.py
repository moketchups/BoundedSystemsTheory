# run_voice_clean.py
# Runs brain_controller.py unchanged, but filters noisy [partial] lines from its output.
# This is pure UX: no logic changes.

from __future__ import annotations

import subprocess
import sys

NOISY_PREFIXES = (
    "[partial]",
)

def main() -> int:
    cmd = [sys.executable, "brain_controller.py"]

    # Run as a subprocess and stream output line-by-line.
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    assert proc.stdout is not None
    try:
        for line in proc.stdout:
            # Filter partial spam
            if line.startswith(NOISY_PREFIXES):
                continue
            # Keep everything else (FINAL, KERNEL_JSON, CONFIRMED, HARDWARE, errors, etc.)
            sys.stdout.write(line)
            sys.stdout.flush()
    except KeyboardInterrupt:
        # Let Ctrl+C stop the child too
        pass
    finally:
        try:
            proc.terminate()
        except Exception:
            pass

    return proc.wait()


if __name__ == "__main__":
    raise SystemExit(main())

