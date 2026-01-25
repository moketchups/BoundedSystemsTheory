#!/usr/bin/env python3
"""
mic_devices.py

Lists PyAudio input devices and their indices.
Use the printed index with:
  DEMERZEL_INPUT_DEVICE_INDEX=<index> python3 mic_vosk_dump.py
"""

def main():
    import pyaudio  # type: ignore
    pa = pyaudio.PyAudio()

    print("Input devices:")
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        max_in = int(info.get("maxInputChannels", 0))
        if max_in > 0:
            name = info.get("name", "")
            rate = info.get("defaultSampleRate", "")
            print(f"  index={i:2d}  inputs={max_in}  rate={rate}  name={name}")

if __name__ == "__main__":
    main()

