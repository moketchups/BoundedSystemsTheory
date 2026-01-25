#!/usr/bin/env python3
"""
wiring_check.py (ACTIVE MODULES ONLY)

Proves the execution-boundary topology for the canonical runtime:

run_*  -> brain_controller.py -> router_engine.py -> kernel_router.py -> hardware_executor.py

Rules:
- Only kernel_router.py may reference hardware_executor
- brain_controller.py must not reference hardware_executor
- router_engine.py must not reference hardware_executor
- router_engine.py must import kernel_router
- hardware_executor.py must not import kernel_router

We IGNORE:
- __lab/, backups/, logs/
- any file with BAK/BROKEN/BACKUP/TEXT_ONLY in its name
"""

from __future__ import annotations

import ast
import os
from typing import List, Set, Tuple

REPO_ROOT = os.path.abspath(os.path.dirname(__file__))

ACTIVE_FILES: Set[str] = {
    "brain_controller.py",
    "router_engine.py",
    "kernel_router.py",
    "hardware_executor.py",
}

IGNORE_DIRS = {".git", "__pycache__", ".venv", "venv", "site-packages", "__lab", "backups", "logs"}
IGNORE_NAME_SUBSTRINGS = {".BAK", ".bak", "BACKUP", "backup", "BROKEN", "TEXT_ONLY", "OLD", "ARCHIVE", "archive"}


def should_ignore_path(path: str) -> bool:
    rel = os.path.relpath(path, REPO_ROOT)
    parts = rel.split(os.sep)
    if any(p in IGNORE_DIRS for p in parts):
        return True
    base = os.path.basename(path)
    if any(s in base for s in IGNORE_NAME_SUBSTRINGS):
        return True
    return False


def parse_file(path: str) -> ast.AST:
    with open(path, "r", encoding="utf-8") as f:
        return ast.parse(f.read(), filename=path)


def find_module_refs(tree: ast.AST, module_name: str) -> List[Tuple[int, str]]:
    hits: List[Tuple[int, str]] = []

    class V(ast.NodeVisitor):
        def visit_Import(self, node: ast.Import) -> None:
            for n in node.names:
                if n.name == module_name:
                    hits.append((node.lineno, f"import {module_name}"))
            self.generic_visit(node)

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            if node.module == module_name:
                hits.append((node.lineno, f"from {module_name} import ..."))
            self.generic_visit(node)

        def visit_Name(self, node: ast.Name) -> None:
            if node.id == module_name:
                hits.append((node.lineno, f"name {module_name}"))
            self.generic_visit(node)

        def visit_Attribute(self, node: ast.Attribute) -> None:
            if isinstance(node.value, ast.Name) and node.value.id == module_name:
                hits.append((node.lineno, f"{module_name}.{node.attr}"))
            self.generic_visit(node)

    V().visit(tree)
    return hits


def imports_module(tree: ast.AST, module_name: str) -> bool:
    return bool(find_module_refs(tree, module_name))


def main() -> int:
    failures: List[str] = []

    # Ensure all active files exist
    for req in ACTIVE_FILES:
        p = os.path.join(REPO_ROOT, req)
        if not os.path.exists(p):
            failures.append(f"[FAIL] Missing required active module: {req}")

    if failures:
        print("\n".join(failures))
        return 1

    for fn in sorted(ACTIVE_FILES):
        path = os.path.join(REPO_ROOT, fn)
        if should_ignore_path(path):
            continue

        try:
            tree = parse_file(path)
        except SyntaxError as e:
            failures.append(f"[FAIL] SyntaxError in {fn}: {e}")
            continue

        # hardware_executor references: only allowed in kernel_router.py
        hw_refs = find_module_refs(tree, "hardware_executor")
        if hw_refs and fn != "kernel_router.py":
            locs = ", ".join([f"line {ln} ({kind})" for ln, kind in hw_refs])
            failures.append(f"[FAIL] hardware_executor referenced in {fn}: {locs}")

        # downstream isolation
        if fn == "hardware_executor.py" and imports_module(tree, "kernel_router"):
            failures.append("[FAIL] hardware_executor.py imports kernel_router (downstream must not depend on gate)")

        # adapter constraints
        if fn == "router_engine.py":
            if imports_module(tree, "hardware_executor"):
                failures.append("[FAIL] router_engine.py imports hardware_executor (adapter must not execute)")
            if not imports_module(tree, "kernel_router"):
                failures.append("[FAIL] router_engine.py does not import kernel_router (adapter not wired)")

        if fn == "brain_controller.py" and imports_module(tree, "hardware_executor"):
            failures.append("[FAIL] brain_controller.py imports hardware_executor (brain must not execute)")

    if failures:
        print("\n".join(failures))
        return 1

    print("[PASS] Wiring topology holds for active modules (no bypass paths).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

