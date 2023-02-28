# Contributing

## Getting started

This project uses [poetry](https://python-poetry.org/) to handle production and
development dependencies.

To install all dependencies, you simply need to run:

```sh
poetry install
```

To run tests:

```sh
poetry run pytest
```

To run the type-checker:

```sh
poetry run mypy
```

To run the formatter:

```sh
poetry run black .
```

To lint the project:

```sh
poetry run pylint sqlschm tests
```

The tests are based on snapshots that are stored in [tests_corpus](tests_corpus).
To generate the corpus run:

```sh
PYTHONPATH="$PWD" python scripts/generate_corpus.py
```

## Commit messages

The project adheres to the [conventional commit specification](https://www.conventionalcommits.org/).

The following commit prefixes are supported:

- `feat:`, a new feature
- `fix:`, a bugfix
- `docs:`, a documentation update
- `test:`, a test update
- `chore:`, project housekeeping
- `perf:`, project performance
- `refactor:`, refactor of the code without change in functionality

See the _git log_ for well-formed messages.

## Changelog

The project [keeps a changelog](https://keepachangelog.com/en/1.0.0/) that document every change that is visible to the user.
