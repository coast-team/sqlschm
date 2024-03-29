# Changelog

This project adheres to [Semantic Versioning][semver].

## 0.8.0 (2022-10-28)

-   BREAKING CHANGES: support for indexes

    sqlschm is now able to parse indexes such as:

    ```sql
    CREATE INDEX person_major_index ON person(age) WHERE major > 18;
    ```

    As a consequence, we renamed `tables` of `sql.Schema` by `items`.
    You can update your code in the following way:

    ```py
    # from
    schema.tables
    # to
    schema.tables()
    ```

    `schema.indexes()` returns all indexes.

-   BREAKING CHANGES: remove sql.Alias

    ```py
    # from
    foreign_key.foreign_table.name

    # to
    foreign_key.foreign_table
    ```

-   Add helper functions

    `sql.referred_columns` allows computing referred columns by a foreign key.
    If referred columns are unspecified, then the function returns
    the columns of the primary key of the foreign table.

    `sql.test_resolve_foreign_key` traverse the graph of references
    until a column that is not a foreign key is found.
    Traversed foreign keys are yield.
    Note that this may produce an endless sequence of foreign keys
    in the case of cyclic foreign keys.

## 0.7.0 (2022-10-25)

-   BREAKING CHANGES: use tuples instead of Sequence abstraction

    This has the advantage to make every object hashable.

-   BREAKING CHANGES: use iterables instead of lists in method return type

    This uniformizes the API and avoids some memory allocation

## 0.6.1 (2022-09-29)

-   Allow schemas with empty statements that end with a semicolon

## 0.6.0 (2022-05-30)

-   Add shortcuts to access column names of a uniqueness constraint

-   Add shortcuts to access generated constraint of a column

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