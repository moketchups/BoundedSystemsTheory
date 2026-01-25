#!/usr/bin/env python3
"""
Quickfix: stop the 'KernelResult not iterable' crash in brain_controller.py
and make memory intercept robust to filler words before "remember"/"recall".

This script patches files IN PLACE (with a .bak backup).
Run:
  python3 quickfix_memory_and_crash.py
Then run your normal loop (e.g. python3 run_voice_clean.py)
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path.home() / "demerzel"
BC = ROOT / "brain_controller.py"
RENG = ROOT / "router_engine.py"

def backup(p: Path) -> None:
    b = p.with_suffix(p.suffix + ".bak")
    if not b.exists():
        b.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

def patch_brain_controller() -> bool:
    if not BC.exists():
        print("[PATCH] brain_controller.py not found:", BC)
        return False

    txt = BC.read_text(encoding="utf-8")

    # Replace the remainder-path block that assumes engine.process returns iterable lines.
    # We match the specific pattern shown in your screenshot.
    pat = re.compile(
        r"""
        (print\(f"\[WAKE\]\s+remainder\s+->\s+'\{remainder\}'"\)\s*\n)   # log line
        (\s*)lines\s*=\s*self\.engine\.process\(remainder\)\s*\n
        \2for\s+ln\s+in\s+lines:\s*\n
        \2\s*print\(ln\)\s*\n
        """,
        re.VERBOSE,
    )

    def repl(m: re.Match) -> str:
        indent = m.group(2)
        return (
            m.group(1)
            + f"{indent}kr = self.engine.process(remainder)\n"
            + f"{indent}print('KERNEL_JSON:')\n"
            + f"{indent}try:\n"
            + f"{indent}    print(json.dumps(kr.to_dict(), indent=2))\n"
            + f"{indent}except Exception:\n"
            + f"{indent}    try:\n"
            + f"{indent}        print(kr.to_dict())\n"
            + f"{indent}    except Exception:\n"
            + f"{indent}        print(kr)\n"
        )

    new, n = pat.subn(repl, txt, count=1)
    if n == 0:
        print("[PATCH] brain_controller.py: could not find the exact remainder/lines loop block to replace.")
        print("        (This is safe; no changes made.)")
        return False

    # Ensure json is imported (brain_controller usually already has it, but be safe)
    if not re.search(r"^\s*import\s+json\s*$", new, flags=re.M):
        # insert after first import block line
        new = re.sub(r"^(import\s+[^\n]+\n)", r"\1import json\n", new, count=1, flags=re.M)

    backup(BC)
    BC.write_text(new, encoding="utf-8")
    print("[PATCH] brain_controller.py: fixed KernelResult iteration crash (backup at brain_controller.py.bak)")
    return True

def patch_router_engine_memory() -> bool:
    if not RENG.exists():
        print("[PATCH] router_engine.py not found:", RENG)
        return False

    txt = RENG.read_text(encoding="utf-8")

    # We patch memory interception to handle filler words before remember/recall.
    # Approach: in _try_memory_intercept (or similarly named), normalize by trimming leading filler
    # and by searching for "remember " / "recall " anywhere in the utterance.
    # If function name differs, we still patch by inserting a helper + a small hook near the top of process().
    added_helper = False
    if "_trim_to_memory_keyword" not in txt:
        helper = r'''
def _trim_to_memory_keyword(norm: str) -> str:
    """
    If STT adds filler words before the real command (e.g. 'our remember ...'),
    trim so parsing starts at 'remember'/'recall' if present.
    """
    norm = (norm or "").strip()
    # Prefer earliest occurrence of remember/recall
    hits = []
    for kw in ("remember ", "recall ", "what is my ", "what's my "):
        i = norm.find(kw)
        if i != -1:
            hits.append(i)
    if not hits:
        return norm
    return norm[min(hits):].strip()
'''
        # Insert helper after imports
        txt2, n = re.subn(r"(\n\n)", r"\n\n" + helper + "\n\n", txt, count=1)
        if n:
            txt = txt2
            added_helper = True

    # Patch inside RouterEngine.process: after norm = _normalize(...)
    # so memory interception sees trimmed norm.
    pat = re.compile(r"(norm\s*=\s*_normalize\([^)]+\)\s*\n)")
    def repl(m: re.Match) -> str:
        return m.group(1) + "        norm = _trim_to_memory_keyword(norm)\n"
    txt2, n2 = pat.subn(repl, txt, count=1)
    if n2 == 0:
        print("[PATCH] router_engine.py: could not locate normalization line inside process(); no changes made.")
        return False

    backup(RENG)
    RENG.write_text(txt2, encoding="utf-8")
    msg = "[PATCH] router_engine.py: made memory commands robust to filler words"
    if added_helper:
        msg += " (helper added)"
    msg += f" (backup at router_engine.py.bak)"
    print(msg)
    return True

def main():
    ok1 = patch_brain_controller()
    ok2 = patch_router_engine_memory()
    if ok1 or ok2:
        print("\nDone. Now run:\n  python3 run_voice_clean.py\n")
    else:
        print("\nNo changes were applied. (Files didn't match expected patterns.)\n")

if __name__ == "__main__":
    main()
