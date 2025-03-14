# T8 API Client

This is a Python client for the T8 REST API.

## Development Setup

1. Clone the repository

```bash
git clone github.com/t8/t8-python-client.git
```

2. Create a virtual environment

```bash
cd t8-python-client
uv venv
```

3. Run the tests

```bash
uv run pytest
```

4. Run the linter

```bash
uv run ruff check
```

5. Execute the client

```bash
uv run t8-client
```