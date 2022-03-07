# Changelog

This project adheres to [Semantic Versioning][semver].

## Unreleased

-   Basic support for parsing CREATE TABLE statement

    Expressions in DEFAULT and CHECK clauses are skipped.

    ```py
    from sqlschm import parse_schema

    statement = """
    CREATE TABLE person(
        fullname text NOT NULL PRIMARY KEY
    );
    """

    schema = parse_schema(statement)
    ```


[semver]: https://semver.org/spec/v2.0.0.html