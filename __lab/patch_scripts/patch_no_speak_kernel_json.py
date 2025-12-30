from pathlib import Path
import re
import sys
from datetime import datetime

p = Path("kernel_router.py")
s = p.read_text()

bak = p.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
bak.write_text(s)

# Replace the two known "speak debug" patterns with print-only logging.
# We keep the debug info, but it must never go through _say().
s2 = s

# 1) _say("KERNEL_JSON:")  -> print("KERNEL_JSON:", flush=True)
s2, n1 = re.subn(
    r"""(^[ \t]*)_say\(\s*["']KERNEL_JSON:\s*["']\s*\)\s*$""",
    r"""\1print("KERNEL_JSON:", flush=True)""",
    s2,
    flags=re.MULTILINE,
)

# 2) _say(kernel_result_to_json_str(result)) -> print(kernel_result_to_json_str(result), flush=True)
s2, n2 = re.subn(
    r"""(^[ \t]*)_say\(\s*kernel_result_to_json_str\(\s*result\s*\)\s*\)\s*$""",
    r"""\1print(kernel_result_to_json_str(result), flush=True)""",
    s2,
    flags=re.MULTILINE,
)

if n1 == 0 and n2 == 0:
    print("[PATCH] No matching KERNEL_JSON speak calls found. No changes made.")
    print(f"[PATCH] Backup still written: {bak.name}")
    sys.exit(2)

p.write_text(s2)
print(f"[PATCH] Disabled speaking KERNEL_JSON debug (print-only now).")
print(f"[PATCH] Backup written: {bak.name}")
