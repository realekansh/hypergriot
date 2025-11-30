# Contributing to HyperGriot

Thanks for your interest in contributing! This project follows clean code conventions, modular architecture, and clear separation of responsibilities.

## Development Rules
1. Keep handlers minimal — NO heavy logic in handlers.
2. Put core logic into services.
3. Always write unit tests for new modules.
4. Don’t introduce new dependencies without discussion.
5. Follow file layout and naming conventions.

## Pull Request Guidelines
- PR must pass `pytest` before merging.
- PR must include updated docs if adding new features.
- PR must not mix unrelated changes.
- PR title must follow:  
  `feat: xxx`, `fix: yyy`, `docs: zzz`, `chore: aaa`

## Code Style
- Use black formatting.
- Type hints required.
- Avoid deeply nested logic.

