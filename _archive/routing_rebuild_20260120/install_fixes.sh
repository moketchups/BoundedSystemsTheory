#!/bin/bash
# DEMERZEL FIX SCRIPT
# Run from anywhere: bash ~/demerzel/install_fixes.sh
# Or: chmod +x ~/demerzel/install_fixes.sh && ~/demerzel/install_fixes.sh

DEMERZEL_DIR="$HOME/demerzel"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=========================================="
echo "DEMERZEL STRUCTURAL FIX INSTALLER"
echo "=========================================="
echo ""

# Step 1: Backup
echo "[1/4] Creating backups..."
cp "$DEMERZEL_DIR/multi_model_cognitive.py" "$DEMERZEL_DIR/multi_model_cognitive_BACKUP_$TIMESTAMP.py"
echo "      Backed up: multi_model_cognitive.py"

# Step 2: Create persistent_state.py
echo "[2/4] Creating persistent_state.py..."
cat > "$DEMERZEL_DIR/persistent_state.py" << 'ENDOFFILE'
# persistent_state.py
# Cross-facet state sharing for Demerzel
# Created: January 14, 2026

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from pathlib import Path


class PersistentStateManager:
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = Path(db_path)
        self._ensure_state_table()
    
    def _ensure_state_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS persistent_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    value_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    expires_at TEXT,
                    metadata TEXT
                )
            """)
            conn.commit()
    
    def set_state(self, key: str, value: Any, expires_minutes: Optional[int] = None, metadata: Dict = None):
        now = datetime.now().isoformat()
        expires_at = None
        if expires_minutes:
            expires_at = (datetime.now() + timedelta(minutes=expires_minutes)).isoformat()
        
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value)
            value_type = "json"
        elif isinstance(value, bool):
            value_str = str(value)
            value_type = "bool"
        elif isinstance(value, (int, float)):
            value_str = str(value)
            value_type = "number"
        else:
            value_str = str(value)
            value_type = "string"
        
        metadata_str = json.dumps(metadata or {})
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO persistent_state 
                (key, value, value_type, created_at, updated_at, expires_at, metadata)
                VALUES (?, ?, ?, COALESCE((SELECT created_at FROM persistent_state WHERE key = ?), ?), ?, ?, ?)
            """, (key, value_str, value_type, key, now, now, expires_at, metadata_str))
            conn.commit()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value, value_type, expires_at FROM persistent_state WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            
            if not row:
                return default
            
            value_str, value_type, expires_at = row
            
            if expires_at:
                expires = datetime.fromisoformat(expires_at)
                if datetime.now() > expires:
                    conn.execute("DELETE FROM persistent_state WHERE key = ?", (key,))
                    conn.commit()
                    return default
            
            if value_type == "json":
                return json.loads(value_str)
            elif value_type == "bool":
                return value_str.lower() == "true"
            elif value_type == "number":
                return float(value_str) if "." in value_str else int(value_str)
            else:
                return value_str
    
    def list_keys(self, pattern: str = None) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            if pattern:
                cursor = conn.execute(
                    "SELECT key FROM persistent_state WHERE key LIKE ? AND (expires_at IS NULL OR expires_at > ?)",
                    (f"%{pattern}%", datetime.now().isoformat())
                )
            else:
                cursor = conn.execute(
                    "SELECT key FROM persistent_state WHERE expires_at IS NULL OR expires_at > ?",
                    (datetime.now().isoformat(),)
                )
            return [row[0] for row in cursor.fetchall()]
    
    def clear_state(self, key: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM persistent_state WHERE key = ?", (key,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_summary(self) -> str:
        keys = self.list_keys()
        if not keys:
            return "No persistent state."
        summary = ["[STATE] Persistent:"]
        for key in keys[:10]:
            value = self.get_state(key)
            summary.append(f"  {key}: {str(value)[:50]}")
        return "\n".join(summary)


_state_manager = None

def get_state_manager(db_path: str = "memory.db") -> PersistentStateManager:
    global _state_manager
    if _state_manager is None:
        _state_manager = PersistentStateManager(db_path)
    return _state_manager
ENDOFFILE
echo "      Created: persistent_state.py"

# Step 3: Patch multi_model_cognitive.py for Claude-only mode
echo "[3/4] Patching multi_model_cognitive.py for Claude-only mode..."

# Find and replace _select_model method
# This is a simple approach - adds a return "claude" at the start of the method
python3 << 'ENDPYTHON'
import re

filepath = "/Users/jamienucho/demerzel/multi_model_cognitive.py"

with open(filepath, 'r') as f:
    content = f.read()

# Check if already patched
if 'CLAUDE-ONLY MODE' in content:
    print("      Already patched!")
else:
    # Find _select_model and insert claude-only return
    pattern = r'(def _select_model\(self\):)\s*\n(\s*)("""[^"]*"""|\'\'\'[^\']*\'\'\'|\#[^\n]*\n)?'
    
    def replacer(match):
        indent = match.group(2) if match.group(2) else '        '
        docstring = match.group(3) if match.group(3) else ''
        return f'''{match.group(1)}
{indent}# CLAUDE-ONLY MODE - other facets broken/unreliable
{indent}return "claude"
{indent}# Original logic below (disabled):
{indent}{docstring}'''
    
    new_content = re.sub(pattern, replacer, content, count=1)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print("      Patched successfully!")
    else:
        print("      Could not find _select_model - manual patch needed")
ENDPYTHON

# Step 4: Test
echo "[4/4] Testing persistent_state.py..."
cd "$DEMERZEL_DIR"
python3 -c "from persistent_state import get_state_manager; m = get_state_manager(); m.set_state('install_test', 'success'); print('      Test:', m.get_state('install_test'))"

echo ""
echo "=========================================="
echo "INSTALLATION COMPLETE"
echo "=========================================="
echo ""
echo "Changes made:"
echo "  1. Created: $DEMERZEL_DIR/persistent_state.py"
echo "  2. Patched: multi_model_cognitive.py (Claude-only mode)"
echo "  3. Backup:  multi_model_cognitive_BACKUP_$TIMESTAMP.py"
echo ""
echo "To test: python3 chat_test.py"
echo "To restore: cp multi_model_cognitive_BACKUP_$TIMESTAMP.py multi_model_cognitive.py"
echo ""
