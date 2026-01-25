# DEMERZEL BASELINE — LOCKED

Date: 2025-12-17

## What is confirmed working
- Local, offline voice assistant
- Wake phrase with fuzzy aliasing
- Immediate acknowledgement on wake
- Post-wake command gate (no premature UNKNOWN)
- FINAL-only speech routing
- Deterministic reasoning kernel
- Explicit confirmation for hardware actions
- Raspberry Pi + Arduino control via SSH
- Deterministic ACK-based hardware responses

## Safety properties
- No action executes without explicit confirmation when required
- No partial speech can trigger actions
- No silent corrections of misheard commands
- Voice is treated as an unreliable shell
- Kernel is the single source of truth

## Known limitations (accepted)
- Vosk partial spam internally (filtered for UX)
- Homophones (led/lead) require confirmation
- No LLM / internet usage

## Do not change without intent
- kernel_contract.py
- router_engine.py
- hardware_executor.py
- arduino_cmd.py
- brain_controller.py (logic)

