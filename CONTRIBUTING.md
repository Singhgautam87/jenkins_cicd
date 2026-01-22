# Contributing Guidelines

## Development Setup

1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd my_jenkins_pipeline
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   make install
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start infrastructure**
   ```bash
   make docker-up
   ```

## Code Standards

- **Type hints**: Use type hints for all function signatures
- **Docstrings**: Add docstrings to all public functions/classes
- **Logging**: Use structured logging via `src.core.logger`
- **Error handling**: Use custom exceptions from `src.core.exceptions`
- **Testing**: Write unit tests for all new features

## Running Tests

```bash
make test
```

## Code Formatting

```bash
make format  # Auto-format code
make lint    # Check code quality
```

## Commit Messages

Follow conventional commits:
- `feat: Add new feature`
- `fix: Fix bug`
- `docs: Update documentation`
- `refactor: Code refactoring`
- `test: Add tests`

## Pull Request Process

1. Create feature branch from `main`
2. Make changes with tests
3. Ensure all tests pass
4. Update documentation
5. Submit PR with clear description
