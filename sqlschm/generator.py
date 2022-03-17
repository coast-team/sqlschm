import textwrap
from sqlschm import sql


def generate_schema(schema: sql.Schema, dialect: sql.Dialect, /) -> str:
    result = ""
    for table in schema.tables:
        result += _generate_create_table(table)
    return result


def _generate_create_table(table: sql.Table, /) -> str:
    table_name = _generate_qualified_name(table.name)
    temp = " TEMPORARY" if table.temporary else ""
    if_not_exists = " IF NOT EXISTS" if table.if_not_exists else ""
    or_replace = " OR REPLACE" if table.or_replace else ""
    strict = " STRICT" if table.options.strict else ""
    without_rowid = " WITHOUT ROWID" if table.options.without_rowid else ""
    body_entries = list(map(_generate_column_def, table.columns)) + list(
        map(_generate_constraint, table.constraints)
    )
    body = ",\n".join(body_entries)
    body = "\n" + textwrap.indent(body, " " * 12)
    return textwrap.dedent(
        f"""
        CREATE{or_replace}{temp} TABLE{if_not_exists} {table_name}({body}
        ){strict}{without_rowid};
        """
    )


def _generate_column_def(col: sql.Column, /) -> str:
    coltype = " " + _generate_type(col.type) if col.type.name != "" else ""
    not_null = " NOT NULL" if col.not_null else ""
    autoincr = " AUTOINCREMENT" if col.autoincrement else ""
    collation = f" COLLATE {col.collation}" if col.collation is not None else ""
    return f"{col.name}{coltype}{not_null}{autoincr}{collation}"


def _generate_constraint(constraint: sql.Constraint, /) -> str:
    if isinstance(constraint, sql.Uniqueness):
        name = f"CONSTRAINT {constraint.name} " if constraint.name is not None else ""
        on_conflict = _generate_on_conflict(constraint.on_conflict)
        if constraint.is_primary:
            return f"{name}PRIMARY KEY ({', '.join(constraint.columns)}){on_conflict}"
        else:
            return f"{name}UNIQUE ({', '.join(constraint.columns)}){on_conflict}"
    else:
        assert isinstance(constraint, sql.ForeignKey)
        foreign_table = _generate_qualified_name(constraint.foreign_table)
        referred_columns = (
            "(" + ", ".join(constraint.referred_columns) + ")"
            if constraint.referred_columns is not None
            else ""
        )
        on_update = _generate_on_update_delete(constraint.on_update, True)
        on_delete = _generate_on_update_delete(constraint.on_delete, False)
        not_deferrable = (
            " NOT DEFERRABLE" if constraint.enforcement.not_deferrable else ""
        )
        initially_deferred = (
            " INITIALLY DEFERRED" if constraint.enforcement.initially_deferred else ""
        )
        return (
            f"FOREIGN KEY ({', '.join(constraint.columns)}) "
            + f"REFERENCES {foreign_table}{referred_columns}"
            + f"{on_update}{on_delete}{not_deferrable}{initially_deferred}"
        )


def _generate_on_conflict(on_conflict: sql.OnConflict, /) -> str:
    if on_conflict is sql.OnConflict.ABORT:
        return ""
    else:
        return f" ON CONFLICT {on_conflict.name}"


def _generate_on_update_delete(action: sql.OnUpdateDelete, on_update: bool, /) -> str:
    if action is sql.OnUpdateDelete.NO_ACTION:
        return ""
    else:
        action_name = action.name.replace("_", " ")
        if on_update:
            return f" ON UPDATE {action_name}"
        else:
            return f" ON DELETE {action_name}"


def _generate_type(type: sql.Type | None, /) -> str:
    if type is not None:
        iter(type.params)
        params = (
            f"({', '.join(map(str, type.params))})" if len(type.params) != 0 else ""
        )
        return type.name.lower() + params
    return ""


def _generate_qualified_name(qualified_name: sql.QualifiedName, /) -> str:
    names = list(qualified_name)
    names.reverse()
    return ".".join(names)
