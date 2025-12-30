from pathlib import Path
import re

p = Path("brain_controller.py")
src = p.read_text()
lines = src.splitlines()

# We know the compiler is complaining around this line from your screenshot.
ERR_LINE_1BASED = 389
err_i = ERR_LINE_1BASED - 1

if err_i < 0 or err_i >= len(lines):
    print("[FIX] Error line out of range; file shorter than expected.")
    raise SystemExit(1)

# Find nearest preceding "try:" that could be enclosing this line.
# We don't require same indent; we choose the closest "try:" above.
try_i = None
for j in range(err_i, -1, -1):
    if lines[j].lstrip().startswith("try:") and lines[j].strip() == "try:":
        try_i = j
        break

if try_i is None:
    print("[FIX] Could not find any 'try:' above line", ERR_LINE_1BASED)
    raise SystemExit(2)

try_indent = len(lines[try_i]) - len(lines[try_i].lstrip(" "))

# Find where the try-block ends (first real line that dedents to <= try_indent)
end_i = None
for k in range(try_i + 1, len(lines)):
    s = lines[k].strip()
    if s == "" or s.startswith("#"):
        continue
    indent_k = len(lines[k]) - len(lines[k].lstrip(" "))
    if indent_k <= try_indent:
        end_i = k
        break

if end_i is None:
    end_i = len(lines)

# Insert a minimal except block at the end of the try suite
except_line = " " * try_indent + "except Exception as e:"
pass_line   = " " * (try_indent + 4) + "pass  # auto-added to close broken try"
insert = [except_line, pass_line]

bak = p.with_suffix(".py.tryfix.bak")
bak.write_text(src)

new_lines = lines[:end_i] + insert + lines[end_i:]
p.write_text("\n".join(new_lines) + "\n")

print(f"[FIX] Found try: at line {try_i+1}, inserted except/pass before line {end_i+1}")
print(f"[FIX] Backup written to: {bak}")
