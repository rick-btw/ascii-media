# Contributing

Contributions are welcome. For substantial changes, open an issue first so the approach can be
discussed.

## Local setup

```bash
git clone https://github.com/rick-btw/ascii-media.git
cd ascii-media
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

Run the checks before opening a pull request:

```bash
ruff check .
pytest
```

Please keep changes focused, include tests for new behavior, and update the README when a user-facing
option changes.
