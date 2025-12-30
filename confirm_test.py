import time
import json
import pyaudio
from vosk import Model, KaldiRecognizer

RATE = 16000
CHUNK = 4000

def main():
    print("Loading Vosk model...")
    model = Model("vosk-model-small-en-us-0.15")

    rec = KaldiRecognizer(model, RATE)
    rec.SetWords(False)

    pa = pyaudio.PyAudio()
    dev_index = pa.get_default_input_device_info()["index"]

    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=dev_index,
    )

    print("\nSay EXACTLY one word: 'confirm' or 'cancel'")
    print("You have 8 seconds. Anything else is ignored.\n")

    deadline = time.time() + 8.0
    heard_final = ""

    while time.time() < deadline:
        data = stream.read(CHUNK, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result() or "{}")
            text = (result.get("text") or "").strip().lower()
            if text:
                print(f"[FINAL] {text}")
                heard_final = text
                break
        else:
            partial = json.loads(rec.PartialResult() or "{}").get("partial", "").strip().lower()
            if partial:
                print(f"[partial] {partial}")

    stream.stop_stream()
    stream.close()
    pa.terminate()

    print("\n=== DECISION ===")
    if heard_final == "confirm":
        print("CONFIRM ✅")
    elif heard_final == "cancel":
        print("CANCEL ✅")
    elif heard_final:
        print(f"HEARD SOMETHING ELSE: '{heard_final}' (This would NOT count as confirm/cancel)")
    else:
        print("HEARD NOTHING (not listening / wrong mic / Vosk not decoding)")
    print("===============")

if __name__ == "__main__":
    main()

