This project uses [poetry][python-poetry] to handle production and
development dependencies.

It uses pytest for unit-testing and black for code formatting.

To install all dependencies, you simply need to run:

```sh
poetry install
```

To run the formatter:

```sh
poetry run black sqlschm/ tests/
```

To run tests:

```sh
poetry run pytest
```

To run the type-checker:

```sh
poetry run pyright
```

To generate the corpus ast:

```sh
PYTHONPATH="$PWD" python scripts/generate_corpus.py
```

[poetry-python]: https://python-poetry.org
