# Changelog

This project adheres to [Semantic Versioning][semver].

## 0.5.0 (2022-04-21)

-   BREAKING CHANGES: Lossless parsing

    The produced AST expose now DEFAULT, GENERATED, and CHECK constraint.

## 0.4.0 (2022-04-15)

-   Expose foreign keys' match value in the AST

-   BREAKING CHANGES: parse and expose indexed columns in the AST

    SQLite enables to specify the collation and the sorting order
    of a column inside a unique or primary key constraint.

    The following schema is now properly parsed:

    ```sql
    CREATE TABLE person(
        fullname NOT NULL,
        PRIMARY KEY (fullname COLLATE BINARY ASC)
    );
    ```

    Collation and sorting order are exported in the the AST.

-   BREAKING CHANGES: more generic AST

    Previously the parser did assumptions about the default values of
    some clause. It now do less assumption and thus it is more generic.

    Some node of the AST accept now None.

## 0.3.0 (2022-04-13)

-   Uniformize sequence types in Schemas

    Previously the schemas used a mix of tuples and lists.
    It now uses a single type: collections.abc.Sequence
    This type is abstract and may represent as well a tuple as a list.
    Moreover, it offers a readonly interface.

## 0.2.1 (2022-04-12)

-   Fix named constraints parsing

    Previously sqlschm failed to parse named constraints.
    Named constraints are now properly parsed. For instance:

    ```sql
    CREATE TABLE person(
        fullname text,
        CONSTRAINT a_name PRIMARY KEY (fullname)
    );
    ```

-   Fix table options generation

    Previously sqlschm forgot to separate table options with a comma.

-   Fix identifier generation

    Previously the generator did not handle keywords as identifiers and
    special strings as identifiers.
    Now it quote every identifier and so handle keyword and special strings
    as identifiers.

## 0.2.0 (2022-03-17)

-   Turn on type-checking for dependant projects

    A type-checker looks for type stubs or `py.typed` file
    in order to consume declared types.

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
    out = generate_schema(schema, Dialect.SQLITE)
    ```

[semver]: https://semver.org/spec/v2.0.0.html