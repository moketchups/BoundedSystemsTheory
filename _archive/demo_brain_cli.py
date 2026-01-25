#!/usr/bin/env python3
import json
from brain import Brain

def main():
    brain = Brain(name="Demerzel", memory_path="brain_memory.json")
    print("\nDemerzel Brain Demo (text-in / audit-out)")
    print("Type messages. Ctrl+C to exit.\n")

    while True:
        try:
            user = input("YOU> ").strip()
        except KeyboardInterrupt:
            print("\nbye")
            break

        out = brain.receive_input(user, source="demo_cli")

        print("\n--- DEMERZEL SAYS ---")
        print(out.speak if out.speak else "(silent)")

        print("\n--- AUDIT TRACE ---")
        print(out.to_json())

        print("\n--- BRAIN STATE ---")
        print(json.dumps(brain.dump_state(), indent=2))
        print("")

if __name__ == "__main__":
    main()

