# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- AI Agent activation: Agents now run `agent_listener.py` and can execute tasks with LLM integration.
- Code application logic: Agents can parse markdown code blocks and write files.
- Example project seeder: `scripts/create_example_project.py` creates a Todo App demo.
- Comprehensive documentation: `docs/tasks_schema.md`, `docs/cursor_integration.md`, `docs/agent_prompts.md`.
- Docker healthchecks for ChromaDB and restart policies for all services.

### Changed
- Enhanced `.env.example` with detailed comments for all configuration options.
- Improved error handling in `watcher.py` and `task_manager.py`.
- Updated `docker-compose.agents.yml` to run agents automatically.

### Fixed
- Robustness improvements to prevent crashes on invalid JSON or transient errors.

## [1.1.0] - 2025-11-19

### Added
- Initial release of the complete Dev_Stack system.
- Docker containerization for 5 agent roles (Taskmaster, Dev1, Dev2, Testing, Review, DevOps).
- Git Worktree integration for conflict-free parallel development.
- `watcher.py` service for event-driven agent orchestration.
- `task_manager.py` CLI for task management.
- RAG integration using ChromaDB and `embed_codebase.py`.
- HTML Dashboard generation.
- Comprehensive documentation in `docs/`.

### Changed
- Refined `README.md` structure.
- Improved Docker Compose configuration for better networking.
