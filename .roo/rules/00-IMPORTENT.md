# Agent-Agnostic Software Design Guide
*(Concise, non-opinionated)*

Use these principles for any build (e.g., app, service, library, script, ML system). Treat everything as guidance; apply only where relevant.

---

## Core Principles
*(The must-remembers)*

* **DRY (Don't Repeat Yourself):** Eliminate duplicated logic; extract shared utilities.

* **Separation of Concerns:** Each module handles one kind of responsibility.

* **Single Responsibility:** One reason to change per class/module/function/file.

* **Clear Abstractions & Contracts:** Expose intent via small, stable interfaces; hide implementation details.

* **Low Coupling, High Cohesion:** Minimize cross-module knowledge; keep related code together.

* **Explicit Boundaries:** Keep core logic independent from I/O, UI, frameworks, storage, and transport.

* **Determinism (where possible):** Prefer pure, side-effect-free functions for core business rules.

* **Idempotency for Actions (when applicable):** Allow safe retries for operations that may be repeated.

* **YAGNI & KISS (You Ain't Gonna Need It & Keep It Simple, Stupid):** Build only what's needed now; keep the solution as simple as possible.