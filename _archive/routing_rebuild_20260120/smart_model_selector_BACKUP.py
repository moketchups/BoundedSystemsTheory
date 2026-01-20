# smart_model_selector.py
# LEARNING-BASED MODEL SELECTION
# Demerzel builds her own preferences through experience
# NO hardcoded affinities - she learns what works

import sqlite3
import json
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from pathlib import Path
import random


class SmartModelSelector:
    """
    Learning-based model selection.
    
    Demerzel starts with NO preferences.
    She tracks success/failure for each model + task combination.
    She builds her own affinity scores through experience.
    She selects based on what SHE has learned works.
    """
    
    MODELS = ["claude", "gpt-4o", "gemini", "grok"]
    FAILURE_THRESHOLD = 2
    FAILURE_WINDOW_MINUTES = 30
    EXPLORATION_RATE = 0.1
    MIN_SAMPLES_FOR_PREFERENCE = 3
    
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = Path(db_path)
        self._ensure_tables()
        self.recent_failures: Dict[str, List[datetime]] = {m: [] for m in self.MODELS}
        self.task_model_scores = self._load_learned_scores()
        print(f"[MODEL SELECTOR] Loaded {len(self.task_model_scores)} learned patterns")
    
    def _ensure_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    model TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    response_time_ms INTEGER,
                    notes TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_task 
                ON model_outcomes(model, task_type)
            """)
            conn.commit()
    
    def _load_learned_scores(self) -> Dict[str, Dict[str, float]]:
        scores = {}
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT task_type, model, COUNT(*) as total, SUM(success) as successes
                FROM model_outcomes
                WHERE timestamp > datetime('now', '-7 days')
                GROUP BY task_type, model
                HAVING total >= ?
            """, (self.MIN_SAMPLES_FOR_PREFERENCE,))
            
            for row in cursor.fetchall():
                task_type, model, total, successes = row
                if task_type not in scores:
                    scores[task_type] = {}
                scores[task_type][model] = successes / total if total > 0 else 0.5
        return scores
    
    def record_outcome(self, model: str, task_type: str, success: bool, 
                       response_time_ms: int = None, notes: str = None):
        """Record outcome - THIS IS HOW I LEARN"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO model_outcomes 
                (timestamp, model, task_type, success, response_time_ms, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), model, task_type, 
                  1 if success else 0, response_time_ms, notes))
            conn.commit()
        
        # Update in-memory scores
        if task_type not in self.task_model_scores:
            self.task_model_scores[task_type] = {}
        current = self.task_model_scores[task_type].get(model, 0.5)
        alpha = 0.3
        self.task_model_scores[task_type][model] = (1-alpha)*current + alpha*(1.0 if success else 0.0)
        
        # Health tracking
        if not success:
            self.recent_failures[model].append(datetime.now())
            cutoff = datetime.now() - timedelta(minutes=self.FAILURE_WINDOW_MINUTES)
            self.recent_failures[model] = [f for f in self.recent_failures[model] if f > cutoff]
        elif self.recent_failures.get(model):
            self.recent_failures[model] = self.recent_failures[model][1:]
        
        print(f"[LEARNING] {model} + {task_type} = {'SUCCESS' if success else 'FAILURE'}")
    
    def is_model_healthy(self, model: str) -> bool:
        cutoff = datetime.now() - timedelta(minutes=self.FAILURE_WINDOW_MINUTES)
        self.recent_failures[model] = [f for f in self.recent_failures.get(model, []) if f > cutoff]
        return len(self.recent_failures.get(model, [])) < self.FAILURE_THRESHOLD
    
    def get_healthy_models(self) -> List[str]:
        return [m for m in self.MODELS if self.is_model_healthy(m)]
    
    def select_model(self, task_type: str = "unknown") -> str:
        """Select model based on health and MY learned preferences"""
        task_type = task_type.lower().strip() if task_type else "unknown"
        
        healthy = self.get_healthy_models()
        if not healthy:
            print("[MODEL HEALTH] All unhealthy. Resetting.")
            self.recent_failures = {m: [] for m in self.MODELS}
            healthy = self.MODELS.copy()
        
        # Exploration
        if random.random() < self.EXPLORATION_RATE:
            selected = random.choice(healthy)
            print(f"[MODEL SELECT] {task_type} → {selected} (EXPLORING)")
            return selected
        
        # Exploitation - use MY learned preference
        task_scores = self.task_model_scores.get(task_type, {})
        scored = {m: task_scores.get(m, 0.5) for m in healthy}
        
        if scored:
            best = max(scored.keys(), key=lambda m: scored[m])
            has_data = task_type in self.task_model_scores and best in self.task_model_scores[task_type]
            if has_data:
                print(f"[MODEL SELECT] {task_type} → {best} (LEARNED: {scored[best]:.0%})")
            else:
                print(f"[MODEL SELECT] {task_type} → {best} (NO DATA YET)")
            return best
        
        selected = random.choice(healthy)
        print(f"[MODEL SELECT] {task_type} → {selected} (RANDOM)")
        return selected
    
    def get_learned_preferences(self) -> str:
        if not self.task_model_scores:
            return "[LEARNING] No preferences yet. Still exploring."
        lines = ["[LEARNING] My learned preferences:"]
        for task, scores in sorted(self.task_model_scores.items()):
            if scores:
                best = max(scores.keys(), key=lambda m: scores[m])
                lines.append(f"  {task}: {best} ({scores[best]:.0%})")
        return "\n".join(lines)
    
    def get_status(self) -> str:
        lines = ["[MODEL STATUS]", "  Health:"]
        for m in self.MODELS:
            s = "✓" if self.is_model_healthy(m) else "✗"
            lines.append(f"    {m}: {s} ({len(self.recent_failures.get(m, []))} failures)")
        lines.append("  Learned:")
        if self.task_model_scores:
            for t, sc in list(self.task_model_scores.items())[:5]:
                if sc:
                    b = max(sc.keys(), key=lambda m: sc[m])
                    lines.append(f"    {t} → {b} ({sc[b]:.0%})")
        else:
            lines.append("    (none yet)")
        return "\n".join(lines)
