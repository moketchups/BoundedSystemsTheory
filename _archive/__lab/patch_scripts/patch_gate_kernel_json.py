from pathlib import Path
import re, sys
from datetime import datetime

p = Path("kernel_router.py")
s = p.read_text()
bak = p.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
bak.write_text(s)

# Ensure we have os imported (light-touch)
if "import os" not in s:
    # put it near the top after first import block
    s = re.sub(r'^(import[^\n]*\n)', r'\1import os\n', s, count=1, flags=re.MULTILINE)

# Gate the print-only KERNEL_JSON block if present
# We look for:
#   print("KERNEL_JSON:", flush=True)
#   print(kernel_result_to_json_str(result), flush=True)
pattern = r'(^[ \t]*)print\("KERNEL_JSON:",\s*flush=True\)\s*\n\1print\(kernel_result_to_json_str\(result\),\s*flush=True\)\s*$'
m = re.search(pattern, s, flags=re.MULTILINE)
if not m:
    print("[PATCH] Could not find print-only KERNEL_JSON block to gate. No changes made.")
    print(f"[PATCH] Backup still written: {bak.name}")
    sys.exit(2)

indent = m.group(1)
replacement = (
    f"{indent}if os.getenv('DEMERZEL_DEBUG_KERNEL_JSON') == '1':\n"
    f"{indent}    print(\"KERNEL_JSON:\", flush=True)\n"
    f"{indent}    print(kernel_result_to_json_str(result), flush=True)\n"
)
s2 = re.sub(pattern, replacement, s, flags=re.MULTILINE)

p.write_text(s2)
print("[PATCH] Gated KERNEL_JSON printing behind DEMERZEL_DEBUG_KERNEL_JSON=1 (default OFF).")
print(f"[PATCH] Backup written: {bak.name}")
