import re, time, shutil, sys
from pathlib import Path

PATH = Path("brain_controller.py")
if not PATH.exists():
    print("ERROR: brain_controller.py not found")
    sys.exit(1)

ts = time.strftime("%Y%m%d_%H%M%S")
bak = PATH.with_name(f"brain_controller.py.BAK_POLICY_V1B_{ts}")
shutil.copy2(PATH, bak)
print("Backup:", bak.name)

s = PATH.read_text(encoding="utf-8", errors="ignore")

# 1) Ensure allowlist exists (explicit contract > heuristic)
if "ALLOWED_SHORT_COMMANDS" not in s:
    m = re.search(r"^(?:import[^\n]*\n|from[^\n]*\n)+\n", s, flags=re.M)
    if not m:
        print("ERROR: Could not locate import block to insert allowlist.")
        print("Revert: cp", bak.name, "brain_controller.py")
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

# 2) Patch the short-final gate by anchoring on the print line you showed
lines = s.splitlines(True)
target_idxs = [i for i,l in enumerate(lines) if "Ignored very short FINAL in COMMAND" in l]

if not target_idxs:
    print("ERROR: Could not find the gate print line: 'Ignored very short FINAL in COMMAND.'")
    print("Revert: cp", bak.name, "brain_controller.py")
    sys.exit(3)

i = target_idxs[0]

# Find the nearest preceding 'if' that references min_final_chars_command / len(ft)
if_idx = None
for j in range(i-1, max(-1, i-12), -1):
    if "min_final_chars_command" in lines[j] or "len(ft)" in lines[j]:
        # walk upward to the actual 'if'
        for k in range(j, max(-1, j-6), -1):
            if re.match(r"^\s*if\s+", lines[k]):
                if_idx = k
                break
    if if_idx is not None:
        break

if if_idx is None:
    print("ERROR: Found the print line but could not locate the 'if' condition above it.")
    print("Revert: cp", bak.name, "brain_controller.py")
    sys.exit(4)

indent = re.match(r"^(\s*)", lines[if_idx]).group(1)

# Remove the whole if-condition header (handles multi-line conditions) up to the colon line
end = if_idx
while end < len(lines):
    if ":" in lines[end]:
        end += 1
        break
    end += 1

new_if = f"{indent}if len(ft) < int(self.cfg.min_final_chars_command) and ft not in ALLOWED_SHORT_COMMANDS:\n"
lines[if_idx:end] = [new_if]
print("OK: rewrote short-command gate condition above the print line")

# 3) Write + compile
out = "".join(lines)
PATH.write_text(out, encoding="utf-8")
print("Wrote brain_controller.py")

import py_compile
py_compile.compile(str(PATH), doraise=True)
print("COMPILES OK")
