# AetherOS - Product Requirements Document
## The Unified Symbolic Operating System
### 7-AI Consensus PRD v1.0

---

## Executive Summary

### Product Name
**AetherOS**

*Consensus Rationale:* "Aether" evokes the foundational, all-pervading medium that unifies the symbolic systems. It is technically plausible, memorable, and carries metaphysical connotations without being overly literal or restrictive.

### One-Line Description
AetherOS is a research operating system that implements core computing primitives through bounded, testable metaphors from symbolic systems—managing resources via Kabbalistic topology, monitoring via I Ching state machines, securing via Gnostic capabilities, and rendering via geometric constraints.

### Core Thesis
This is not a general-purpose consumer OS. It is a **research and experimentation platform** built to test a specific hypothesis: that esoteric symbolic systems can provide coherent, practical, and measurable abstractions for operating system design. Value is derived from the concrete implementation, instrumentation, and analysis of these coded metaphors.

---

## What It Does

AetherOS is a novel operating system built from the ground up, integrating symbolic and metaphysical systems into a functional OS architecture:

| Ancient System | OS Function | Implementation |
|---|---|---|
| **Kabbalah (Sefirot)** | Kernel + File System | Tree of Life directory structure, process scheduling |
| **I Ching** | System Telemetry | 64 hexagrams = 64 discrete system states |
| **Sacred Geometry** | Rendering Engine | Flower of Life UI constraints, geometric compositing |
| **Gnosticism** | Access Control | Archon sandboxes, Gnosis = root access |
| **3-6-9 Vortex Math** | Compression/Hashing | Digital root modulo-9 algorithms |
| **Phoenix Cycle** | Memory Management | Birth/Death/Rebirth garbage collection |
| **The Ark** | Backup/Storage | Immutable snapshots, disaster recovery |

### Why It Matters

AetherOS challenges conventional OS design by proving that esoteric principles can create coherent, measurable computing systems. It serves as:

1. **A Research Platform** - Test whether symbolic systems provide valid computing abstractions
2. **A Functional OS** - For developers, artists, researchers, and alternative computing enthusiasts
3. **An Educational Tool** - Explore the intersection of ancient wisdom and modern computation

---

## Product Architecture Overview

AetherOS employs a **hybrid kernel architecture**: a monolithic core for performance, with well-defined, modular subsystems communicating via IPC.

### Architectural Philosophy

- **Bounded Metaphors:** Each subsystem implements a specific, testable metaphor. The mapping from symbolic concept to technical implementation must be explicit and falsifiable.
- **POSIX-like Compatibility:** Where possible, subsystems expose familiar POSIX interfaces.
- **Instrumentation First:** Every subsystem must expose metrics to evaluate the "efficacy" of its core metaphor.

### Subsystem Map & Dependencies

```
[Bootloader] -> [KABBALAH Kernel] -> [PHOENIX Memory Manager]
      |                  |                  |
      v                  v                  v
[I CHING Telemetry]  [GNOSTIC Security]  [Userland Init]
      |                  |                  |
      v                  v                  v
[VORTEX Compression] <-> [ARK Storage]  [SACRED GEOMETRY Compositor]
```

---

## Detailed Subsystem Specifications

### 1. KABBALAH Subsystem: Kernel & Topological File System
**Project Name:** `kernel-sefirot`

**Primary Function:** Process scheduling, Virtual File System (VFS), and Inter-Process Communication (IPC).

**Core Metaphor:** The Tree of Life (10 Sefirot, 22 Paths) provides the topology for system organization and policy propagation.

**Technical Specification:**
- **Language:** Rust (primary), with minimal assembly for boot and low-level operations
- **Scheduler:** The 10 Sefirot map to scheduler policy classes. Process Control Blocks (PCBs) are extended with a `sefirah: u8` field:
  - `Keter` (1): Real-time, highest priority
  - `Chokmah` (2): Wisdom processes, high CPU
  - `Binah` (3): Understanding processes, memory-intensive
  - `Chesed` (4): Grace/expansion, high I/O bandwidth
  - `Gevurah` (5): Strict CPU/time limits
  - `Tiferet` (6): Balanced/standard processes
  - `Netzach` (7): Persistent/long-running
  - `Hod` (8): Communication/networking
  - `Yesod` (9): I/O-bound favoring
  - `Malkuth` (10): Background/batch
- **VFS (Sefirot-FS):** Modified ext4 foundation. Root (`/`) is `Ain Soph`. Primary directories are the Sefirot:
  ```
  /
  ├── keter/      # System core, protected
  ├── chokmah/    # Wisdom, AI/ML models
  ├── binah/      # Understanding, documentation
  ├── chesed/     # Grace, user data
  ├── gevurah/    # Strength, security policies
  ├── tiferet/    # Beauty, applications
  ├── netzach/    # Victory, persistent services
  ├── hod/        # Splendor, networking
  ├── yesod/      # Foundation, system libraries
  └── malkuth/    # Kingdom, user space
  ```
- **System Daemons:** Named after Angelic Orders (e.g., `seraphimd` (network), `ophanimd` (storage))

**MVP Deliverable:** Bootable kernel in QEMU with functional VFS where Sefirot directories are navigable. Round-robin scheduler that reads process `sefirah` tags.

---

### 2. I CHING Subsystem: Entropy & State Telemetry
**Project Name:** `telemetry-hexagram`

**Primary Function:** Real-time system monitoring, health scoring, and entropy measurement.

**Core Metaphor:** 64 Hexagrams represent discrete, comprehensible states of a complex system.

**Technical Specification:**
- **Language:** C (for low-level polling), with a Rust API layer
- **State Model:** Six critical boolean system conditions form a 6-bit mask:
  1. `CPU_OVERLOAD` (avg load > 0.8)
  2. `MEMORY_CRITICAL` (free < 10%)
  3. `DISK_FULL` (root fs usage > 90%)
  4. `NETWORK_DOWN` (no default route)
  5. `HIGH_ENTROPY` (unpredictable I/O pattern)
  6. `USER_ACTIVE` (recent input)
- **Service (`ichingd`):** Userspace daemon polling `/proc` and sysfs every second. Computes current hexagram ID (0-63) and Unicode symbol (e.g., ䷀ "The Creative")
- **API:** Data published to:
  - Kernel ring buffer (`/proc/hexagram`)
  - IPC message bus for other subsystems
  - `libiching` for applications: `get_hexagram() -> (id, symbol, changing_lines)`

**Example Output:**
```
$ cat /proc/hexagram
䷀ 1 "The Creative" CPU:OK MEM:OK DISK:OK NET:OK ENTROPY:LOW USER:ACTIVE
```

**MVP Deliverable:** `ichingd` running as PID 2, monitoring CPU and memory, writing hexagram to `/proc/hexagram`.

---

### 3. SACRED GEOMETRY Subsystem: Constrained Rendering
**Project Name:** `compositor-metatron`

**Primary Function:** Windowing system, display compositor, and graphical output.

**Core Metaphor:** Visual space is structured according to the Flower of Life and Metatron's Cube patterns.

**Technical Specification:**
- **Language:** C++ with Vulkan/OpenGL backend
- **Compositor (`metatron`):** Wayland-protocol compatible compositor
- **Constraint Engine:** Screen mapped to hexagonal grid derived from Seed of Life:
  - Window dimensions and positions "snap" to this grid
  - Maximizing triggers "Metatron's Cube" tiling pattern
  - Window animations follow geodesic paths on the grid
- **`libgeometry`:** Library providing vertex buffers for sacred geometric shapes

**MVP Deliverable:** Placeholder binary displaying static Flower of Life grid. Full implementation post-MVP.

---

### 4. GNOSTICISM Subsystem: Capability-Based Security
**Project Name:** `security-pleroma`

**Primary Function:** User authentication, privilege management, and access control.

**Core Metaphor:** Material world (user space) is managed by "Archons," while "Gnosis" grants root access.

**Technical Specification:**
- **Language:** Rust
- **Archon Sandboxes:** Untrusted apps run via `archon-run`, creating lightweight containers with restricted capabilities
- **Pleroma Capabilities:** Process authority defined by unforgeable capability tokens:
  - `CAP_NET_BIND`
  - `CAP_FILE_WRITE:/chesed/*`
  - `CAP_PROCESS_SPAWN`
- **Gnosis Attainment:** Superuser privileges via cryptographic challenge-response:
  - Kernel provides nonce from current hexagram + system secret
  - User responds with valid signature from key in `/etc/gnosis/keys`
- **Privilege Levels:**
  - `Hyletic` - Standard user (material)
  - `Psychic` - Elevated admin (soul)
  - `Pneumatic` - Full gnosis/root (spirit)

**MVP Deliverable:** Basic capability checks on syscalls. `gnosis` user exists. Working `archon-run` command.

---

### 5. VORTEX MATH Subsystem: Compression & Hashing
**Project Name:** `codec-vortex`

**Primary Function:** Lossless data compression and cryptographic hashing.

**Core Metaphor:** Data patterns encoded using digital root (modulus 9) mathematics and 3-6-9 cycles.

**Technical Specification:**
- **Language:** Optimized C with inline assembly
- **Algorithm (`vortex9`):**
  1. Maintains sliding window of last N bytes
  2. Calculates digital root (iterated sum mod 9) of window
  3. Uses root (0-9) to select encoding dictionary
  4. Finite-state machine favors 3→6→9 cycle transitions
- **Use Cases:** `initrd` compression, `vzip`/`vunzip` tools, kernel hashing

**MVP Deliverable:** Library with basic algorithm that can compress test files. Performance optimization post-MVP.

---

### 6. PHOENIX CYCLE Subsystem: Memory Management
**Project Name:** `mm-phoenix`

**Primary Function:** Physical and virtual memory allocation, page management, garbage collection.

**Core Metaphor:** Memory has lifecycle of Birth (allocation), Death (release), Rebirth (re-use).

**Technical Specification:**
- **Language:** Rust
- **Three-Zone Physical Allocator:**
  1. **Nest Zone:** Fresh, zeroed pages. First choice for new allocations
  2. **Flight Zone:** Actively mapped, "living" pages
  3. **Ash Zone:** Pages unmapped (died) but held in cache
- **Daemon (`phoenixd`):** Kernel thread scanning Ash zone. If accessed page ("spark"), promotes back to Flight
- **Garbage Collector:** Mark-and-sweep for kernel objects, tracing through Sefirot topology

**MVP Deliverable:** Basic buddy allocator with three-zone labeling. `phoenixd` placeholder.

---

### 7. THE ARK Subsystem: Backup & Recovery
**Project Name:** `storage-ark`

**Primary Function:** System snapshot, backup, and state restoration.

**Core Metaphor:** Preserving system state against "flood" of data loss.

**Technical Specification:**
- **Language:** Python (orchestration) calling Rust libraries
- **Tool (`ark`):** Userspace utility
- **Snapshot Process:**
  1. Flush caches via `phoenixd`
  2. Serialize Sefirot-FS metadata and Pleroma capabilities
  3. Compress via `vortex9`
  4. Package as bootable disk image
- **Recovery:** Boot from snapshot to restore exact state

**MVP Deliverable:** Script creating tarball of root filesystem. Full bootable image post-MVP.

---

## User Stories

1. **Systems Researcher:** "I want to spawn processes tagged with different Sefirot and measure if their CPU/IO align with policy classes."

2. **Security Auditor:** "I want to run untrusted binaries in Archon sandboxes and log denied syscalls."

3. **Developer:** "I want to compile my project, compress with `vortex9`, and compare to gzip."

4. **System Admin:** "I want to see Hexagram ䷝ (The Wanderer) in my status bar indicating high entropy."

5. **Artist:** "I want Metatron's Cube window layout for my drawing application."

6. **Consciousness Researcher:** "I want to study how symbolic computing abstractions compare to traditional ones."

---

## Technical Specifications

### Languages
- **Rust:** Kernel, security, memory management
- **C:** Telemetry, low-level polling
- **C++:** Rendering, compositor
- **Python:** Tooling, backup orchestration

### Build System
- Toolchain: `rustc`, `gcc`, `nasm`, `cmake`
- Boot: Multiboot2-compliant kernel, GRUB2 or EFI
- Target: x86_64 (QEMU primary), AArch64 (secondary)

### Key Data Structures
```rust
struct SefirahProcessDescriptor {
    pid: u32,
    sefirah: u8,           // 1-10 mapping to Sefirot
    capabilities: PleromaCapSet,
    state: ProcessState,
}

struct HexagramState {
    id: u8,                // 0-63
    symbol: [char; 4],     // Unicode hexagram
    conditions: u8,        // 6-bit bitmask
    changing_lines: u8,    // Which lines are changing
}

struct PleromaCapSet {
    tokens: RadixTree<CapabilityToken>,
    level: PrivilegeLevel,  // Hyletic, Psychic, Pneumatic
}

struct PhoenixPageFrame {
    frame_id: u64,
    zone: Zone,            // Nest, Flight, Ash
    last_access: Timestamp,
}
```

### Repository Structure
```
aetheros/
├── kernel/           # kernel-sefirot
├── telemetry/        # telemetry-hexagram
├── security/         # security-pleroma
├── compositor/       # compositor-metatron
├── codec/            # codec-vortex
├── memory/           # mm-phoenix
├── backup/           # storage-ark
├── tools/            # CLI utilities
└── docs/             # Documentation
```

---

## MVP Scope

**Primary Goal:** Bootable system in QEMU (x86_64) demonstrating integrated core metaphors.

### MVP Deliverables (Priority 1)

1. **`kernel-sefirot`:**
   - Boots on QEMU
   - Sefirot-FS with `/keter`, `/binah`, `/malkuth` navigable
   - Round-robin scheduler with `sefirah` tag support

2. **`telemetry-hexagram`:**
   - `ichingd` daemon running
   - Monitors CPU/Memory
   - Writes hexagram to `/proc/hexagram`

3. **`security-pleroma`:**
   - Basic capability checks on syscalls
   - `gnosis` user (password bypass for MVP)
   - Working `archon-run` for sandboxing

4. **Integrated Demo (`init` process):**
   - Spawns processes with different `sefirah` tags
   - Reads and prints current hexagram
   - Demonstrates capability denial
   - Clean shutdown

### Post-MVP
- Sacred Geometry Compositor (full)
- Vortex Compression (optimized)
- Phoenix Memory Manager (full)
- Ark Backup (bootable images)

---

## Success Metrics

1. **Boot Reliability:** MVP boots in QEMU >95% of the time
2. **Metaphor Fidelity:**
   - Sefirot-FS navigable via `ls /`, `cat /proc/hexagram`
   - Hexagram changes in response to load
   - Archon sandbox blocks forbidden syscalls
3. **Stability:** Demo runs 1 hour without kernel panic
4. **Research Foundation:** Codebase documented for third-party experiments

---

## Open Source Strategy

### License
**GNU General Public License v3.0 (GPLv3)**

Ensures the research platform remains open and modifications are shared back, critical for collaborative validation.

### Repository
- Hosted on GitHub
- Issues and PRs welcome
- Clear contribution guidelines

### Community
- Target: Academic OS researchers, digital humanities, esoteric programming enthusiasts
- Documentation: Technical specs + philosophical rationale for each subsystem

### Governance
Lightweight meritocracy. Core architectural decisions maintained by consensus. Changes to core metaphors require RFC process.

---

## Appendix: AI Consensus

This PRD was developed through collaborative deliberation of 7 AI systems:
- GPT-4o
- Claude (Sonnet)
- Gemini
- DeepSeek
- Grok
- Mistral
- Claude Opus 4.5 (synthesis)

### Key Consensus Points
1. All agreed on seven-subsystem architecture
2. All agreed on research-oriented (not consumer) focus
3. All agreed on open-source release
4. "AetherOS" selected as name (4/6 vote)
5. Rust selected for kernel (safety)
6. GPLv3 selected for licensing

### Disagreements Resolved
- **Kernel type:** Hybrid/monolithic for MVP practicality
- **MVP scope:** Focused on boot, VFS, telemetry, security
- **Deferred:** Full rendering, compression optimization, advanced memory

---

*Document Version: 1.0*
*Date: February 3, 2026*
*Consensus: 6/6 AI approval*
