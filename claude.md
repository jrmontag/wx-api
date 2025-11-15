# Application
- `uv run fastapi dev` - run the main application in development mode
- `uv run fastapi run` - run the main application in production mode

# Style
- `uv run ruff check` - run the linter
- `uv run ruff check --fix` - automatically fix any easy linting issues
- `uv run ruff format` - format the code

# Run tests
- `uv run pytest -v tests` - run the integration test suite

# Workflow 
- After each change, run the linter and reformat the code 
- If there is a test suite, also run the tests after each change; correct any issues
- After each task, ask for confirmation and then commit the changes
