from router_engine import RouterEngine
from hardware_executor import HardwareExecutor, default_config

def main() -> None:
    eng = RouterEngine(HardwareExecutor(default_config()))
    print("Demerzel REPL. Type text, Ctrl-C to exit.")
    while True:
        try:
            text = input("> ").strip()
        except KeyboardInterrupt:
            print("\nbye")
            return
        out = eng.route_text(text)
        if out.speak:
            print(out.speak)
        if out.sleep_mode:
            print("(sleep mode)")

if __name__ == "__main__":
    main()

