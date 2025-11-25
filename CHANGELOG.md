# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
