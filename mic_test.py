import time
import pyaudio
import audioop

RATE = 16000
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

def main():
    pa = pyaudio.PyAudio()

    # Pick default input device
    dev_index = pa.get_default_input_device_info()["index"]
    dev_info = pa.get_device_info_by_index(dev_index)

    print("=== DEFAULT INPUT DEVICE ===")
    print(f"index={dev_index}")
    print(f"name={dev_info.get('name')}")
    print(f"maxInputChannels={dev_info.get('maxInputChannels')}")
    print("============================")

    stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=dev_index,
    )

    print("Talk. You should see RMS numbers change when you speak. Ctrl+C to stop.")
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            rms = audioop.rms(data, 2)  # 2 bytes per sample
            print(f"rms={rms}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopping...")

    stream.stop_stream()
    stream.close()
    pa.terminate()

if __name__ == "__main__":
    main()

