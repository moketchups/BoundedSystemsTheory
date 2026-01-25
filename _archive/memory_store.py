import json, os, time, re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

def _now_ts() -> float:
    return time.time()

# ---------- spoken normalization helpers ----------

_WORD_MAP = {
    "zero":"0","one":"1","two":"2","three":"3","four":"4","five":"5",
    "six":"6","seven":"7","eight":"8","nine":"9",
    "at":"@","dot":".","underscore":"_","dash":"-"
}

def normalize_spoken(text: str) -> str:
    t = text.lower().strip()

    # common email cleanup
    t = t.replace("g male", "gmail")
    t = t.replace("g mail", "gmail")
    t = t.replace("out look", "outlook")

    parts = []
    for w in t.split():
        parts.append(_WORD_MAP.get(w, w))

    out = "".join(
        p if p in "@._-" or p.isalnum() else p
        for p in parts
    )

    # final cleanup
    out = re.sub(r"\s+", "", out)
    return out

# ---------- memory store ----------

@dataclass
class MemoryStore:
    path: str
    data: Dict[str, Any] = field(default_factory=dict)

    def load(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
        self.data.setdefault("facts", {})
        self.data.setdefault("notes", [])

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def remember_fact(self, key: str, value: str) -> None:
        clean = normalize_spoken(value)
        self.data["facts"][key.strip().lower()] = {
            "value": clean,
            "raw": value,
            "ts": _now_ts()
        }
        self.save()

    def remember_note(self, text: str) -> None:
        self.data["notes"].append({"text": text.strip(), "ts": _now_ts()})
        self.data["notes"] = self.data["notes"][-200:]
        self.save()

    def recall_fact(self, key: str) -> Optional[str]:
        item = self.data.get("facts", {}).get(key.strip().lower())
        return item["value"] if item else None

    def recall_all_facts(self) -> Dict[str, str]:
        return {k: v.get("value", "") for k, v in self.data.get("facts", {}).items()}

    def recall_recent_notes(self, n: int = 5) -> List[str]:
        notes = self.data.get("notes", [])[-n:]
        return [x.get("text", "") for x in notes if x.get("text")]
