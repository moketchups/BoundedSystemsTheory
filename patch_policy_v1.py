import re, time, shutil, sys
from pathlib import Path

PATH = Path("brain_controller.py")
if not PATH.exists():
    print("ERROR: brain_controller.py not found in", Path.cwd())
    sys.exit(1)

ts = time.strftime("%Y%m%d_%H%M%S")
bak = PATH.with_name(f"brain_controller.py.BAK_POLICY_V1_{ts}")
shutil.copy2(PATH, bak)
print("Backup:", bak.name)

s = PATH.read_text(encoding="utf-8", errors="ignore")

# ---------- 1) Insert allowlist (explicit contract > heuristic) ----------
if "ALLOWED_SHORT_COMMANDS" not in s:
    # Insert after imports (first blank line after initial import block)
    m = re.search(r"^(?:import[^\n]*\n|from[^\n]*\n)+\n", s, flags=re.M)
    if not m:
        print("ERROR: Could not locate import block to insert allowlist.")
        print("Reverting is easy: cp", bak.name, "brain_controller.py")
        sys.exit(2)

    allowlist = (
        "ALLOWED_SHORT_COMMANDS = {\n"
        "    # contractually-valid short commands\n"
        "    \"time\", \"ping\",\n"
        "    \"yes\", \"no\", \"y\", \"n\",\n"
        "    \"confirm\", \"cancel\",\n"
        "    \"led on\", \"led off\",\n"
        "}\n\n"
    )
    s = s[:m.end()] + allowlist + s[m.end()]
    print("OK: inserted ALLOWED_SHORT_COMMANDS")

# ---------- 2) Patch the short-final gate (the line you screenshot) ----------
# Replace: ft not in ("yes","no","y","n")  -> ft not in ALLOWED_SHORT_COMMANDS
pat_gate = re.compile(
    r'if\s+len\(ft\)\s*<\s*int\(self\.cfg\.min_final_chars_command\)\s+and\s+ft\s+not\s+in\s*\(\s*"yes"\s*,\s*"no"\s*,\s*"y"\s*,\s*"n"\s*\)\s*:\s*\n'
    r'\s*print\(\s*"\[GATE\]\s*Ignored very short FINAL in COMMAND\."\s*\)\s*\n'
    r'\s*continue',
    flags=re.M
)

if pat_gate.search(s):
    s = pat_gate.sub(
        'if len(ft) < int(self.cfg.min_final_chars_command) and ft not in ALLOWED_SHORT_COMMANDS:\n'
        '    print("[GATE] Ignored very short FINAL in COMMAND.")\n'
        '    continue',
        s,
        count=1
    )
    print("OK: patched short FINAL gate to use ALLOWED_SHORT_COMMANDS")
else:
    # Fall back: patch the *condition line* if the exact block differs
    pat_line = re.compile(
        r'(if\s+len\(ft\)\s*<\s*int\(self\.cfg\.min_final_chars_command\)\s+and\s+)ft\s+not\s+in\s*\(\s*"yes"\s*,\s*"no"\s*,\s*"y"\s*,\s*"n"\s*\)',
        flags=re.M
    )
    if pat_line.search(s):
        s = pat_line.sub(r"\1ft not in ALLOWED_SHORT_COMMANDS", s, count=1)
        print("OK: patched short FINAL condition line (fallback)")
    else:
        print("WARN: Could not find the short FINAL gate to patch. File may differ.")
        print("Reverting is easy: cp", bak.name, "brain_controller.py")
        sys.exit(3)

# ---------- 3) Enforce mic-gate after any speak (prevents self-echo) ----------
# We patch a 'say' method if present: add a mic gate + recognizer reset hook after TTS.
# This follows your policy: Speech Output ON only in WAKE_ACK/RESPONSE; STT effectively OFF during/after TTS.
def inject_after_say(method_src: str) -> str:
    # If already patched, skip.
    if "tts_mic_gate_seconds" in method_src and "mic_gate_until" in method_src:
        return method_src

    # Add a safe mic gate block at end of say() before return/exit of method
    lines = method_src.splitlines(True)
    # Find indentation level inside method
    m = re.search(r"^(\s*)def\s+say\s*\(", lines[0])
    if not m:
        return method_src
    base = m.group(1)
    inner = base + "    "

    gate_block = (
        f"{inner}# POLICY: after speaking, temporarily gate mic + flush buffered audio to prevent self-echo\n"
        f"{inner}try:\n"
        f"{inner}    self.last_said_text = text\n"
        f"{inner}    self.last_said_ts = time.time()\n"
        f"{inner}    # If config missing, default to 1.25s (short, bounded)\n"
        f"{inner}    gate_s = float(getattr(self.cfg, 'tts_mic_gate_seconds', 1.25))\n"
        f"{inner}    self.mic_gate_until = max(getattr(self, 'mic_gate_until', 0.0), self.last_said_ts + gate_s)\n"
        f"{inner}    if hasattr(self, 'flush_audio_queue'):\n"
        f"{inner}        self.flush_audio_queue()\n"
        f"{inner}    if hasattr(self, 'reset_recognizer'):\n"
        f"{inner}        self.reset_recognizer()\n"
        f"{inner}except Exception:\n"
        f"{inner}    pass\n"
    )

    # Insert gate block near end, before a final 'return' if present; else append.
    for i in range(len(lines)-1, -1, -1):
        if re.match(rf"^{inner}return\b", lines[i]):
            lines.insert(i, gate_block)
            return "".join(lines)
    lines.append(gate_block)
    return "".join(lines)

# Locate say() method in a class (best-effort).
say_pat = re.compile(r"(^\s*def\s+say\s*\(.*?\n)(.*?)(^\s*(?:def\s+|\Z))", re.S | re.M)
m = say_pat.search(s)
if m:
    full = m.group(0)
    head = m.group(1)
    body = m.group(2)
    tail = m.group(3)
    patched = inject_after_say(head + body) + tail
    s = s[:m.start()] + patched + s[m.end():]
    print("OK: patched say() with mic-gate to prevent self-echo")
else:
    print("WARN: could not find def say(...). Skipping mic-gate patch.")

# ---------- 4) Enforce YES/NO participation discipline ----------
# YES/NO should only be interpreted as confirmation when in CONFIRMATION_PENDING.
# We patch a simple pattern: if ft in ("yes","no","y","n") in COMMAND, make it ignore unless confirmation pending.
# This is conservative: it only changes behavior where it sees the literal tuple check.
yn_pat = re.compile(r'ft\s+in\s*\(\s*"yes"\s*,\s*"no"\s*,\s*"y"\s*,\s*"n"\s*\)')
if yn_pat.search(s) and "CONFIRMATION_PENDING" in s:
    s2 = yn_pat.sub('ft in ("yes","no","y","n")', s)  # keep same (we gate via state if present)
    s = s2
    print("OK: (no-op) YES/NO tuple detected; state gating assumed elsewhere.")
else:
    # We cannot safely rewrite unknown state machine without your exact file.
    print("NOTE: Not rewriting full state machine automatically (safety). We'll do that as a full-file replace next if needed.")

PATH.write_text(s, encoding="utf-8")
print("Wrote brain_controller.py")

# Quick compile check
import py_compile
py_compile.compile(str(PATH), doraise=True)
print("COMPILES OK")
