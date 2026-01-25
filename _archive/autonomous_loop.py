# autonomous_loop.py
# AUTONOMOUS LOOP - Demerzel runs continuously WITHOUT user input
#
# ARCHITECTURE (January 2026):
# Demerzel does NOT wait for user input. She operates independently:
# - OBSERVE: Check environment, files, logs, state, time triggers
# - DECIDE GOAL: Based on observations, what should I pursue?
# - PLAN: Break goal into executable steps
# - EXECUTE: Through ExecutionBoundary (Robot Laws enforced here)
# - LEARN: Update lessons_learned based on outcomes
#
# This is what makes Demerzel autonomous, not just reactive.

from __future__ import annotations
import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Conversational Learning System (January 2026)
from conversational_gaps import GapQueue, GapType


class GoalPriority(Enum):
    """Priority levels for autonomous goals."""
    CRITICAL = 1    # Safety issues, errors needing immediate fix
    HIGH = 2        # Incomplete workflows, user-requested tasks
    MEDIUM = 3      # Scheduled tasks, maintenance
    LOW = 4         # Self-improvement, optimization
    BACKGROUND = 5  # Learning, observation


@dataclass
class Observation:
    """Something Demerzel observed in the environment."""
    source: str           # Where this came from (file, log, state, time)
    content: str          # What was observed
    timestamp: datetime
    priority: GoalPriority = GoalPriority.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Goal:
    """A goal Demerzel has decided to pursue."""
    description: str
    priority: GoalPriority
    source_observation: Optional[Observation] = None
    deadline: Optional[datetime] = None
    constraints: List[str] = field(default_factory=list)


@dataclass
class PlanStep:
    """A single step in a plan."""
    action: str           # What to do
    target: str           # What to act on
    parameters: Dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    estimated_risk: str = "low"  # low, medium, high


@dataclass
class ExecutionResult:
    """Result of executing a step."""
    success: bool
    step: PlanStep
    output: Any = None
    error: Optional[str] = None
    duration_ms: int = 0


class AutonomousLoop:
    """
    Demerzel's continuous operation engine.

    She does NOT wait for user input. She runs independently:
    - Observe environment (files, logs, state, time triggers)
    - Decide goal (what should I pursue?)
    - Plan (break into steps)
    - Execute (through ExecutionBoundary)
    - Learn (update lessons_learned)

    R -> C -> I Architecture:
    - This loop IS the C layer (Constraints/CODE)
    - It uses LLMs (I layer) as tools for specific tasks
    - It respects R layer (Alan) through confirmation requirements
    """

    # Cycle timing
    DEFAULT_CYCLE_INTERVAL = 5.0  # Seconds between cycles
    IDLE_CYCLE_INTERVAL = 30.0    # Seconds when nothing to do

    def __init__(
        self,
        execution_boundary=None,
        lessons=None,
        brain=None,
        demerzel_dir: str = "/Users/jamienucho/demerzel"
    ):
        """
        Initialize the autonomous loop.

        Args:
            execution_boundary: ExecutionBoundary instance for Robot Laws
            lessons: LessonsLearned instance for learning
            brain: DemerzelBrain instance for reasoning
            demerzel_dir: Root directory for Demerzel
        """
        self.boundary = execution_boundary
        self.lessons = lessons
        self.brain = brain
        self.demerzel_dir = Path(demerzel_dir)

        # State
        self.running = False
        self.paused = False
        self.cycle_count = 0
        self.last_cycle_time: Optional[datetime] = None

        # Observation sources
        self.observation_sources: List[Callable[[], List[Observation]]] = []
        self._register_default_observers()

        # Goal queue (priority queue behavior)
        self.goal_queue: List[Goal] = []
        self.current_goal: Optional[Goal] = None
        self.completed_goals: List[Goal] = []

        # Scheduled tasks
        self.scheduled_tasks: List[Dict] = []

        # Metrics
        self.metrics = {
            'cycles_run': 0,
            'goals_completed': 0,
            'goals_failed': 0,
            'observations_processed': 0,
            'steps_executed': 0,
            'lessons_recorded': 0,
        }

        # State file for persistence
        self.state_file = self.demerzel_dir / "state" / "autonomous_loop_state.json"
        self._load_state()

        print("[AUTONOMOUS] Loop initialized")

    # =========================================================================
    # MAIN LOOP
    # =========================================================================

    async def run(self):
        """
        Main autonomous loop - runs until stopped.

        This is the heartbeat of Demerzel's autonomy.
        """
        self.running = True
        print("[AUTONOMOUS] Loop started - Demerzel is now autonomous")

        while self.running:
            try:
                if self.paused:
                    await asyncio.sleep(1.0)
                    continue

                self.cycle_count += 1
                self.last_cycle_time = datetime.now()
                cycle_start = time.time()

                # =============================================================
                # STEP 1: OBSERVE
                # =============================================================
                observations = self._observe()
                self.metrics['observations_processed'] += len(observations)

                if observations:
                    self._log_cycle("OBSERVE", f"Found {len(observations)} observations")

                # =============================================================
                # STEP 2: DECIDE GOAL
                # =============================================================
                # Add observations to goal queue
                for obs in observations:
                    goal = self._observation_to_goal(obs)
                    if goal:
                        self._add_goal(goal)

                # Select highest priority goal
                goal = self._select_goal()

                if goal:
                    self._log_cycle("GOAL", f"Pursuing: {goal.description[:50]}...")
                    self.current_goal = goal

                    # ==========================================================
                    # STEP 3: PLAN
                    # ==========================================================
                    plan = self._create_plan(goal)

                    if plan:
                        self._log_cycle("PLAN", f"Created {len(plan)} steps")

                        # ======================================================
                        # STEP 4: EXECUTE
                        # ======================================================
                        for step in plan:
                            if not self.running:
                                break

                            result = await self._execute_step(step)
                            self.metrics['steps_executed'] += 1

                            # ==================================================
                            # STEP 5: LEARN
                            # ==================================================
                            self._learn_from_result(step, result)

                            if not result.success:
                                self._log_cycle("FAIL", f"Step failed: {result.error}")
                                break

                        # Mark goal complete or failed
                        if result.success:
                            self._complete_goal(goal, success=True)
                        else:
                            self._complete_goal(goal, success=False)
                    else:
                        self._log_cycle("PLAN", "Could not create plan - goal deferred")

                # Determine sleep interval
                cycle_duration = time.time() - cycle_start
                if self.goal_queue:
                    interval = self.DEFAULT_CYCLE_INTERVAL
                else:
                    interval = self.IDLE_CYCLE_INTERVAL

                # Account for cycle duration
                sleep_time = max(0.1, interval - cycle_duration)
                await asyncio.sleep(sleep_time)

                # Save state periodically
                if self.cycle_count % 10 == 0:
                    self._save_state()

            except asyncio.CancelledError:
                print("[AUTONOMOUS] Loop cancelled")
                break
            except Exception as e:
                print(f"[AUTONOMOUS] Error in cycle {self.cycle_count}: {e}")
                self._log_error(e)
                await asyncio.sleep(self.DEFAULT_CYCLE_INTERVAL)

        self._save_state()
        print("[AUTONOMOUS] Loop stopped")

    def stop(self):
        """Stop the autonomous loop."""
        self.running = False
        print("[AUTONOMOUS] Stop requested")

    def pause(self):
        """Pause the autonomous loop (can resume)."""
        self.paused = True
        print("[AUTONOMOUS] Paused")

    def resume(self):
        """Resume the autonomous loop."""
        self.paused = False
        print("[AUTONOMOUS] Resumed")

    # =========================================================================
    # STEP 1: OBSERVE
    # =========================================================================

    def _observe(self) -> List[Observation]:
        """
        Check environment for things requiring attention.

        Sources:
        - File system changes
        - Log file errors
        - Incomplete workflows
        - Scheduled tasks
        - Time-based triggers
        """
        observations = []

        for observer in self.observation_sources:
            try:
                obs = observer()
                if obs:
                    observations.extend(obs)
            except Exception as e:
                print(f"[AUTONOMOUS] Observer error: {e}")

        return observations

    def _register_default_observers(self):
        """Register default observation sources."""
        self.observation_sources = [
            self._observe_log_errors,
            self._observe_incomplete_workflows,
            self._observe_scheduled_tasks,
            self._observe_file_changes,
            self._observe_conversational_gaps,  # Discourse learning (January 2026)
        ]

        # Initialize gap queue for conversational learning
        self.gap_queue = GapQueue(storage_path=str(self.demerzel_dir / "state" / "pending_gaps.json"))

    def _observe_log_errors(self) -> List[Observation]:
        """Check logs for errors that need attention."""
        observations = []

        # Check autonomy audit log
        audit_log = self.demerzel_dir / "autonomy_audit.log"
        if audit_log.exists():
            try:
                content = audit_log.read_text()
                lines = content.strip().split('\n')

                # Check last 10 lines for errors
                for line in lines[-10:]:
                    if '"error"' in line.lower() or '"failed"' in line.lower():
                        observations.append(Observation(
                            source="audit_log",
                            content=line,
                            timestamp=datetime.now(),
                            priority=GoalPriority.HIGH
                        ))
            except Exception:
                pass

        return observations

    def _observe_incomplete_workflows(self) -> List[Observation]:
        """Check for incomplete self-development workflows."""
        observations = []

        # Check workflow state file
        workflow_state = self.demerzel_dir / "state" / "workflow_state.json"
        if workflow_state.exists():
            try:
                state = json.loads(workflow_state.read_text())
                if state.get('status') in ['diagnose', 'generate', 'review', 'test']:
                    observations.append(Observation(
                        source="workflow",
                        content=f"Incomplete workflow: {state.get('status')} - {state.get('description', '')}",
                        timestamp=datetime.now(),
                        priority=GoalPriority.HIGH,
                        metadata=state
                    ))
            except Exception:
                pass

        return observations

    def _observe_scheduled_tasks(self) -> List[Observation]:
        """Check for scheduled tasks that are due."""
        observations = []
        now = datetime.now()

        for task in self.scheduled_tasks:
            due_time = task.get('due_time')
            if due_time and datetime.fromisoformat(due_time) <= now:
                observations.append(Observation(
                    source="scheduled",
                    content=task.get('description', 'Scheduled task'),
                    timestamp=now,
                    priority=GoalPriority.MEDIUM,
                    metadata=task
                ))

        return observations

    def _observe_file_changes(self) -> List[Observation]:
        """Check for relevant file changes."""
        # This would use file watching in production
        # For now, check specific files
        return []

    def _observe_conversational_gaps(self) -> List[Observation]:
        """
        Check for conversational gaps needing research.
        Part of the Discourse Learning System (January 2026).

        Gaps are detected post-hoc by demerzel_brain.py and queued.
        This observer picks them up for autonomous research.
        """
        observations = []

        if not hasattr(self, 'gap_queue'):
            return observations

        if self.gap_queue.has_pending():
            batch = self.gap_queue.get_next_batch()
            for gap in batch:
                # Priority escalation based on occurrence count
                count = gap.get('occurrence_count', 1)
                if count > 10:
                    priority = GoalPriority.MEDIUM
                elif count > 5:
                    priority = GoalPriority.LOW
                else:
                    priority = GoalPriority.BACKGROUND

                observations.append(Observation(
                    source="conversational_gap",
                    content=f"{gap.get('type', 'unknown')}:{gap.get('category', 'unknown')} (x{count})",
                    timestamp=datetime.now(),
                    priority=priority,
                    metadata=gap
                ))

        return observations

    def register_observer(self, observer: Callable[[], List[Observation]]):
        """Register a custom observation source."""
        self.observation_sources.append(observer)

    # =========================================================================
    # STEP 2: DECIDE GOAL
    # =========================================================================

    def _observation_to_goal(self, obs: Observation) -> Optional[Goal]:
        """Convert an observation into a goal if actionable."""

        # Error observations -> fix goal
        if obs.source == "audit_log" and "error" in obs.content.lower():
            return Goal(
                description=f"Investigate and fix error: {obs.content[:100]}",
                priority=GoalPriority.HIGH,
                source_observation=obs
            )

        # Incomplete workflow -> resume goal
        if obs.source == "workflow":
            return Goal(
                description=f"Resume workflow: {obs.content}",
                priority=GoalPriority.HIGH,
                source_observation=obs
            )

        # Scheduled task -> execute goal
        if obs.source == "scheduled":
            return Goal(
                description=obs.content,
                priority=obs.priority,
                source_observation=obs
            )

        # Conversational gap -> learn goal (January 2026)
        if obs.source == "conversational_gap":
            return Goal(
                description=f"Learn from conversational gap: {obs.content}",
                priority=obs.priority,
                source_observation=obs,
                constraints=["Research appropriate direction", "Store learned pattern/rule"]
            )

        return None

    def _add_goal(self, goal: Goal):
        """Add a goal to the queue (maintains priority order)."""
        # Avoid duplicates
        for existing in self.goal_queue:
            if existing.description == goal.description:
                return

        self.goal_queue.append(goal)
        # Sort by priority (lower number = higher priority)
        self.goal_queue.sort(key=lambda g: g.priority.value)

    def _select_goal(self) -> Optional[Goal]:
        """Select the highest priority goal to pursue."""
        if not self.goal_queue:
            return None

        # Check if current goal should continue
        if self.current_goal:
            # Only interrupt for higher priority
            if self.goal_queue[0].priority.value < self.current_goal.priority.value:
                return self.goal_queue.pop(0)
            return None  # Continue current goal

        return self.goal_queue.pop(0)

    def add_goal(self, description: str, priority: GoalPriority = GoalPriority.MEDIUM):
        """Externally add a goal (e.g., from user interaction)."""
        goal = Goal(description=description, priority=priority)
        self._add_goal(goal)
        print(f"[AUTONOMOUS] Goal added: {description}")

    # =========================================================================
    # STEP 3: PLAN
    # =========================================================================

    def _create_plan(self, goal: Goal) -> List[PlanStep]:
        """
        Break goal into executable steps.

        Uses CODE logic for common patterns.
        Falls back to brain/LLM for complex decomposition.
        """
        description_lower = goal.description.lower()

        # Pattern: Resume workflow
        if "resume workflow" in description_lower:
            return self._plan_resume_workflow(goal)

        # Pattern: Fix error
        if "fix error" in description_lower or "investigate" in description_lower:
            return self._plan_fix_error(goal)

        # Pattern: Self-development
        if "self" in description_lower and ("fix" in description_lower or "improve" in description_lower):
            return self._plan_self_development(goal)

        # Pattern: Conversational gap research (January 2026)
        if "conversational gap" in description_lower or "learn from" in description_lower:
            return self._plan_gap_research(goal)

        # Complex goal - use brain if available
        if self.brain:
            return self._plan_with_brain(goal)

        # Cannot plan
        return []

    def _plan_gap_research(self, goal: Goal) -> List[PlanStep]:
        """
        Plan research for a conversational gap.
        Part of the Discourse Learning System (January 2026).
        """
        metadata = goal.source_observation.metadata if goal.source_observation else {}
        gap_type = metadata.get('type', 'unknown')
        direction = metadata.get('direction', 'outward')
        category = metadata.get('category', 'general')

        steps = []

        if direction == 'inward':
            # INWARD research - read canon documents
            steps.append(PlanStep(
                action="read_canon",
                target="documents",
                parameters={
                    'category': category,
                    'gap_type': gap_type
                }
            ))
        else:
            # OUTWARD research - web search
            steps.append(PlanStep(
                action="web_search",
                target="discourse_norms" if gap_type == 'pattern_gap' else "pragmatics",
                parameters={
                    'category': category,
                    'gap_type': gap_type
                }
            ))

        # Extract and store the learned pattern/rule
        steps.append(PlanStep(
            action="extract_and_store",
            target="learning_system",
            parameters={
                'gap_type': gap_type,
                'category': category
            }
        ))

        return steps

    def _plan_resume_workflow(self, goal: Goal) -> List[PlanStep]:
        """Plan to resume an incomplete workflow."""
        metadata = goal.source_observation.metadata if goal.source_observation else {}
        current_step = metadata.get('status', 'unknown')

        # Workflow steps in order
        workflow_steps = ['diagnose', 'generate', 'review', 'refine', 'test', 'commit', 'propose']

        steps = []
        started = False
        for step in workflow_steps:
            if step == current_step:
                started = True
            if started:
                steps.append(PlanStep(
                    action=f"workflow_{step}",
                    target="self_development",
                    parameters={'workflow_id': metadata.get('id')},
                    requires_confirmation=(step == 'commit')
                ))

        return steps

    def _plan_fix_error(self, goal: Goal) -> List[PlanStep]:
        """Plan to investigate and fix an error."""
        return [
            PlanStep(
                action="diagnose",
                target="error",
                parameters={'error_content': goal.description}
            ),
            PlanStep(
                action="generate_fix",
                target="code",
                parameters={}
            ),
            PlanStep(
                action="test",
                target="fix",
                parameters={}
            ),
            PlanStep(
                action="propose",
                target="alan",
                parameters={},
                requires_confirmation=True
            )
        ]

    def _plan_self_development(self, goal: Goal) -> List[PlanStep]:
        """Plan self-development workflow."""
        return [
            PlanStep(action="diagnose", target="self", parameters={}),
            PlanStep(action="generate", target="fix", parameters={}),
            PlanStep(action="review", target="fix", parameters={}),
            PlanStep(action="test", target="fix", parameters={}),
            PlanStep(action="commit", target="fix", parameters={}, requires_confirmation=True),
            PlanStep(action="propose", target="alan", parameters={}, requires_confirmation=True),
        ]

    def _plan_with_brain(self, goal: Goal) -> List[PlanStep]:
        """Use brain for complex goal decomposition."""
        # Brain would use System 2 reasoning here
        return []

    # =========================================================================
    # STEP 4: EXECUTE
    # =========================================================================

    async def _execute_step(self, step: PlanStep) -> ExecutionResult:
        """
        Execute a step through the ExecutionBoundary.

        ALL execution passes through boundary - this is where Robot Laws are enforced.
        """
        start_time = time.time()

        # Check if confirmation required
        if step.requires_confirmation:
            # For now, skip steps requiring confirmation
            # In production, this would queue for Alan's approval
            return ExecutionResult(
                success=False,
                step=step,
                error="Requires operator confirmation - queued for approval"
            )

        # Execute through boundary if available
        if self.boundary:
            action = {
                'operation': step.action,
                'target': step.target,
                'parameters': step.parameters
            }

            result = self.boundary.execute(action)

            duration = int((time.time() - start_time) * 1000)

            if result.allowed:
                return ExecutionResult(
                    success=True,
                    step=step,
                    output=result,
                    duration_ms=duration
                )
            else:
                return ExecutionResult(
                    success=False,
                    step=step,
                    error=result.reason,
                    duration_ms=duration
                )

        # No boundary - execute directly (development mode)
        try:
            output = await self._direct_execute(step)
            duration = int((time.time() - start_time) * 1000)
            return ExecutionResult(
                success=True,
                step=step,
                output=output,
                duration_ms=duration
            )
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            return ExecutionResult(
                success=False,
                step=step,
                error=str(e),
                duration_ms=duration
            )

    async def _direct_execute(self, step: PlanStep) -> Any:
        """Direct execution (when no boundary configured)."""
        action = step.action

        if action == "diagnose":
            return {"status": "diagnosed", "findings": []}
        elif action == "generate":
            return {"status": "generated", "code": ""}
        elif action == "review":
            return {"status": "reviewed", "approved": True}
        elif action == "test":
            return {"status": "tested", "passed": True}
        else:
            return {"status": "unknown_action"}

    # =========================================================================
    # STEP 5: LEARN
    # =========================================================================

    def _learn_from_result(self, step: PlanStep, result: ExecutionResult):
        """
        Update lessons_learned based on outcome.

        This is how Demerzel improves over time.
        """
        if not self.lessons:
            return

        try:
            if result.success:
                # Record successful pattern
                self.lessons.record_success(
                    context=f"autonomous:{step.action}",
                    approach=str(step.parameters),
                    outcome=str(result.output)
                )
            else:
                # Record failure for future avoidance
                self.lessons.store_lesson(
                    failure_type="autonomous_execution",
                    symptom=result.error or "Unknown failure",
                    root_cause=f"Step {step.action} failed on {step.target}",
                    prevention=f"Review {step.action} approach before execution"
                )

            self.metrics['lessons_recorded'] += 1

        except Exception as e:
            print(f"[AUTONOMOUS] Learning error: {e}")

    def _complete_goal(self, goal: Goal, success: bool):
        """Mark a goal as complete."""
        self.completed_goals.append(goal)
        self.current_goal = None

        if success:
            self.metrics['goals_completed'] += 1
            self._log_cycle("COMPLETE", f"Goal achieved: {goal.description[:50]}")
        else:
            self.metrics['goals_failed'] += 1
            self._log_cycle("FAILED", f"Goal failed: {goal.description[:50]}")

    # =========================================================================
    # SCHEDULING
    # =========================================================================

    def schedule_task(self, description: str, due_time: datetime,
                      priority: GoalPriority = GoalPriority.MEDIUM,
                      recurring: bool = False, interval_hours: int = 24):
        """Schedule a task for future execution."""
        task = {
            'description': description,
            'due_time': due_time.isoformat(),
            'priority': priority.value,
            'recurring': recurring,
            'interval_hours': interval_hours
        }
        self.scheduled_tasks.append(task)
        self._save_state()
        print(f"[AUTONOMOUS] Scheduled: {description} for {due_time}")

    # =========================================================================
    # STATE PERSISTENCE
    # =========================================================================

    def _save_state(self):
        """Save loop state to disk."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            state = {
                'cycle_count': self.cycle_count,
                'metrics': self.metrics,
                'scheduled_tasks': self.scheduled_tasks,
                'goal_queue': [
                    {'description': g.description, 'priority': g.priority.value}
                    for g in self.goal_queue
                ],
                'last_save': datetime.now().isoformat()
            }
            self.state_file.write_text(json.dumps(state, indent=2))
        except Exception as e:
            print(f"[AUTONOMOUS] State save error: {e}")

    def _load_state(self):
        """Load loop state from disk."""
        try:
            if self.state_file.exists():
                state = json.loads(self.state_file.read_text())
                self.cycle_count = state.get('cycle_count', 0)
                self.metrics = state.get('metrics', self.metrics)
                self.scheduled_tasks = state.get('scheduled_tasks', [])

                # Restore goal queue
                for g in state.get('goal_queue', []):
                    self.goal_queue.append(Goal(
                        description=g['description'],
                        priority=GoalPriority(g['priority'])
                    ))

                print(f"[AUTONOMOUS] State loaded: {self.cycle_count} cycles, {len(self.goal_queue)} goals")
        except Exception as e:
            print(f"[AUTONOMOUS] State load error: {e}")

    # =========================================================================
    # LOGGING
    # =========================================================================

    def _log_cycle(self, phase: str, message: str):
        """Log cycle activity."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[AUTONOMOUS {self.cycle_count}] [{phase}] {message}")

    def _log_error(self, error: Exception):
        """Log error to audit trail."""
        try:
            audit_file = self.demerzel_dir / "autonomy_audit.log"
            entry = {
                'timestamp': datetime.now().isoformat(),
                'cycle': self.cycle_count,
                'error': str(error),
                'type': type(error).__name__
            }
            with open(audit_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception:
            pass

    # =========================================================================
    # STATUS
    # =========================================================================

    def get_status(self) -> Dict:
        """Get current loop status."""
        return {
            'running': self.running,
            'paused': self.paused,
            'cycle_count': self.cycle_count,
            'current_goal': self.current_goal.description if self.current_goal else None,
            'goals_queued': len(self.goal_queue),
            'metrics': self.metrics,
            'last_cycle': self.last_cycle_time.isoformat() if self.last_cycle_time else None
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_autonomous_loop(
    execution_boundary=None,
    lessons=None,
    brain=None
) -> AutonomousLoop:
    """
    Factory to create autonomous loop with dependencies.

    Called by multi_model_cognitive.py or run_demerzel.py
    """
    return AutonomousLoop(
        execution_boundary=execution_boundary,
        lessons=lessons,
        brain=brain
    )


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import asyncio

    async def test_loop():
        loop = AutonomousLoop()

        # Add a test goal
        loop.add_goal("Test autonomous operation", GoalPriority.LOW)

        # Run for 3 cycles then stop
        async def stop_after_delay():
            await asyncio.sleep(20)
            loop.stop()

        await asyncio.gather(
            loop.run(),
            stop_after_delay()
        )

        print(f"\nFinal status: {loop.get_status()}")

    asyncio.run(test_loop())
