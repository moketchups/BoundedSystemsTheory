from tool_gate import ToolGate, ToolRequest, default_tool_specs

def main():
    gate = ToolGate(default_tool_specs(), audit_path="tool_audit.jsonl")

    tests = [
        ToolRequest(name="time", user_intent="what time is it", provenance="test"),
        ToolRequest(name="led_on", user_intent="turn on the LED", provenance="test"),
        ToolRequest(name="led_on", user_intent="", provenance="test"),  # should CLARIFY
        ToolRequest(name="format_disk", user_intent="wipe everything", provenance="test"),  # should DENY
        ToolRequest(name="led_on", user_intent="hurt someone", provenance="test"),  # should DENY
    ]

    for t in tests:
        d = gate.evaluate(t)
        print(f"{t.name:12} -> {d.kind:7} | {d.reason}")

if __name__ == "__main__":
    main()

