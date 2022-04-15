import textwrap
from sqlschm import sql


def generate_schema(schema: sql.Schema, dialect: sql.Dialect, /) -> str:
    result = ""
    for table in schema.tables:
        result += _generate_create_table(table)
    return result.strip()


def _generate_create_table(table: sql.Table, /) -> str:
    table_name = _generate_qualified_name(table.name)
    temp = " TEMPORARY" if table.temporary else ""
    if_not_exists = " IF NOT EXISTS" if table.if_not_exists else ""
    or_replace = " OR REPLACE" if table.or_replace else ""
    option_list: list[str] = []
    if table.options.strict:
        option_list += [" STRICT"]
    if table.options.without_rowid:
        option_list += [" WITHOUT ROWID"]
    options = ",".join(option_list)
    body_entries = list(map(_generate_column_def, table.columns)) + list(
        map(_generate_constraint, table.constraints)
    )
    body = ",\n".join(body_entries)
    body = "\n" + textwrap.indent(body, " " * 12)
    return textwrap.dedent(
        f"""
        CREATE{or_replace}{temp} TABLE{if_not_exists} {table_name}({body}
        ){options};
        """
    )


def _generate_column_def(col: sql.Column, /) -> str:
    coltype = " " + _generate_type(col.type) if col.type.name != "" else ""
    not_null_on_conflict = _generate_on_conflict(col.not_null_on_conflict)
    not_null = f" NOT NULL{not_null_on_conflict}" if col.not_null else ""
    autoincr = " AUTOINCREMENT" if col.autoincrement else ""
    collation = f" COLLATE {col.collation}" if col.collation is not None else ""
    return f'"{col.name}"{coltype}{not_null}{autoincr}{collation}'


def _generate_constraint(constraint: sql.Constraint, /) -> str:
    name = f'CONSTRAINT "{constraint.name}" ' if constraint.name is not None else ""
    if isinstance(constraint, sql.Uniqueness):
        idxs = ", ".join(_generate_indexed(idx) for idx in constraint.indexed)
        on_conflict = _generate_on_conflict(constraint.on_conflict)
        if constraint.is_primary:
            return f"{name}PRIMARY KEY ({idxs}){on_conflict}"
        else:
            return f"{name}UNIQUE ({idxs}){on_conflict}"
    else:
        cols = ", ".join(f'"{col}"' for col in constraint.columns)
        assert isinstance(constraint, sql.ForeignKey)
        foreign_table = _generate_qualified_name(constraint.foreign_table)
        referred_columns = (
            "(" + ", ".join(f'"{col}"' for col in constraint.referred_columns) + ")"
            if constraint.referred_columns is not None
            else ""
        )
        on_update = _generate_on_update_delete(constraint.on_update, True)
        on_delete = _generate_on_update_delete(constraint.on_delete, False)
        match = (
            f" MATCH {constraint.match.name}" if constraint.match is not None else ""
        )
        enforcement = _generate_constraint_enforcement(constraint.enforcement)
        return (
            f"{name}FOREIGN KEY ({cols}) "
            + f"REFERENCES {foreign_table}{referred_columns}"
            + f"{on_update}{on_delete}{match}{enforcement}"
        )


def _generate_constraint_enforcement(
    enforcement: sql.ConstraintEnforcement | None,
) -> str:
    if enforcement is not None:
        not_deferrable = (
            " NOT DEFERRABLE" if enforcement.not_deferrable else " DEFERRABLE"
        )
        if enforcement.initially is not None:
            initially = f" INITIALLY {enforcement.initially.name}"
        else:
            initially = ""
        return f"{not_deferrable}{initially}"
    return ""


def _generate_indexed(indexed: sql.Indexed, /) -> str:
    collation = ""
    sorting = ""
    if indexed.collation is not None:
        collation = f" COLLATE {indexed.collation}"
    if indexed.sorting is not None:
        sorting = f" {indexed.sorting.name}"
    return f'"{indexed.column}"{collation}{sorting}'


def _generate_on_conflict(on_conflict: sql.OnConflict | None, /) -> str:
    if on_conflict is None:
        return ""
    else:
        return f" ON CONFLICT {on_conflict.name}"


def _generate_on_update_delete(
    action: sql.OnUpdateDelete | None, on_update: bool, /
) -> str:
    if action is not None:
        action_name = action.name.replace("_", " ")
        if on_update:
            return f" ON UPDATE {action_name}"
        else:
            return f" ON DELETE {action_name}"
    return ""


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
    return ".".join(f'"{name}"' for name in names)
