#!/usr/bin/env python3
import sys
import time
import glob
import os

import serial  # pyserial

BAUD = 115200
READ_TIMEOUT = 2.5

# Arduino often auto-resets when the serial port is opened.
# Give it time to reboot, then drain any boot chatter.
BOOT_WAIT_SEC = 1.2
DRAIN_WINDOW_SEC = 1.0

# Retry behavior for flaky first command after reset
TRIES = 3

def find_port() -> str | None:
    # Prefer a stable symlink if you have one
    if os.path.exists("/dev/arduino"):
        return "/dev/arduino"

    ports = sorted(glob.glob("/dev/ttyACM*")) + sorted(glob.glob("/dev/ttyUSB*"))
    if not ports:
        return None
    return ports[0]

def normalize_line(line: str) -> str:
    line = (line or "").strip()
    if not line:
        return "ACK ERR NO_RESPONSE"

    # If Arduino already speaks in ACK/ERR, don’t double-wrap.
    if line.startswith("ACK "):
        return line
    if line.startswith("ACK"):
        return line  # e.g. "ACK" alone
    if line.startswith("ERR"):
        return "ACK " + line  # enforce top-level ACK for the Mac side

    # Default: treat any text as an ACK payload
    return "ACK " + line

def open_serial(port: str) -> serial.Serial:
    ser = serial.Serial(
        port=port,
        baudrate=BAUD,
        timeout=READ_TIMEOUT,
        write_timeout=READ_TIMEOUT,
    )

    # Let Arduino reboot after DTR-triggered reset
    time.sleep(BOOT_WAIT_SEC)

    # Drain boot lines (if any) so our first read corresponds to our command
    end = time.time() + DRAIN_WINDOW_SEC
    try:
        while time.time() < end:
            if ser.in_waiting:
                _ = ser.readline()
            else:
                time.sleep(0.05)
    except Exception:
        pass

    # Clear buffers
    try:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
    except Exception:
        pass

    return ser

def send_once(cmd: str) -> str:
    port = find_port()
    if not port:
        return "ACK ERR NO_SERIAL_PORT"

    ser = None
    try:
        ser = open_serial(port)
        ser.write((cmd + "\n").encode("ascii", errors="ignore"))
        ser.flush()

        line = ser.readline().decode("ascii", errors="ignore")
        return normalize_line(line)

    except Exception as e:
        return f"ACK ERR {type(e).__name__}:{e}"
    finally:
        try:
            if ser:
                ser.close()
        except Exception:
            pass

def main() -> int:
    if len(sys.argv) < 2:
        print("ACK ERR NO_COMMAND")
        return 1

    # Support commands that may have been passed as multiple argv parts
    cmd = " ".join(sys.argv[1:]).strip()
    if not cmd:
        print("ACK ERR EMPTY_COMMAND")
        return 1

    last = "ACK ERR UNKNOWN"
    for _ in range(TRIES):
        last = send_once(cmd)
        # If we got any non-empty ACK that isn’t NO_RESPONSE, accept it.
        if "NO_RESPONSE" not in last and "NO_SERIAL_PORT" not in last:
            print(last)
            return 0
        time.sleep(0.25)

    print(last)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
