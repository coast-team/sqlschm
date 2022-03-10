# Changelog

This project adheres to [Semantic Versioning][semver].

## 0.1.0 (2022-03-10)

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

-   Basic support for generating CREATE TABLE from a schema

    Only SQLite dialect is available.

    ```py
    from sqlschm import generate_schema, Dialect

    # schema is obtained from a parsing step
    out = generate_schema(schema, Dialect;SQLITE)
    ```

[semver]: https://semver.org/spec/v2.0.0.html