from typing import Iterable
import textwrap
from sqlschm import sql, tok


def generate_schema(schema: sql.Schema, dialect: sql.Dialect, /) -> str:
    result = ""
    for item in schema.items:
        if isinstance(item, sql.Table):
            result += _generate_create_table(item)
        else:
            result += _generate_create_index(item)
    return result.strip()


def _generate_create_index(index: sql.Index, /) -> str:
    index_name = _generate_qualified_name(index.name)
    unique = " UNIQUE" if index.unique else ""
    if_not_exists = " IF NOT EXISTS" if index.if_not_exists else ""
    idxs = ", ".join(_generate_indexed(idx) for idx in index.indexed)
    where = f" WHERE {_generate_tokens(index.where)}" if index.where is not None else ""
    return textwrap.dedent(
        f"""
        CREATE{unique} INDEX{if_not_exists} {index_name} ON "{index.table}"({idxs}){where};
        """
    )


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
        map(_generate_table_constraint, table.constraints)
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
    constraints = "".join(_generate_column_constraint(x) for x in col.constraints)
    return f'"{col.name}"{coltype}{constraints}'


def _generate_column_constraint(constraint: sql.ColumnConstraint, /) -> str:
    name = f' CONSTRAINT"{constraint.name}" ' if constraint.name is not None else ""
    if isinstance(constraint, sql.Uniqueness):
        on_conflict = _generate_on_conflict(constraint.on_conflict)
        if constraint.is_primary:
            sorting = constraint.indexed[0].sorting
            sorting_str = f"{sorting.name}" if sorting is not None else ""
            autoinc = " AUTOINCREMENT" if constraint.autoincrement else ""
            return f"{name} PRIMARY KEY{sorting_str}{on_conflict}{autoinc}"
        else:
            return f"{name} UNIQUE{on_conflict}"
    elif isinstance(constraint, sql.ForeignKey):
        fk_clause = _generate_foreign_key_clause(constraint)
        return f"{name} {fk_clause}"
    elif isinstance(constraint, sql.Check):
        expr = _generate_tokens(constraint.expr)
        return f"{name} CHECK ({expr})"
    elif isinstance(constraint, sql.NotNull):
        on_conflict = _generate_on_conflict(constraint.on_conflict)
        return f"{name} NOT NULL{on_conflict}"
    elif isinstance(constraint, sql.Default):
        expr = _generate_tokens(constraint.expr)
        return f"{name} DEFAULT {expr}"
    elif isinstance(constraint, sql.Collation):
        return f"{name} COLLATE {constraint.value}"
    else:
        kind = f" {constraint.kind.name}" if constraint.kind is not None else ""
        expr = _generate_tokens(constraint.expr)
        return f"{name} GENERATED ALWAYS AS ({expr}){kind}"


def _generate_table_constraint(constraint: sql.TableConstraint, /) -> str:
    name = f'CONSTRAINT "{constraint.name}" ' if constraint.name is not None else ""
    if isinstance(constraint, sql.Uniqueness):
        idxs = ", ".join(_generate_indexed(idx) for idx in constraint.indexed)
        on_conflict = _generate_on_conflict(constraint.on_conflict)
        if constraint.is_primary:
            return f"{name}PRIMARY KEY ({idxs}){on_conflict}"
        else:
            return f"{name}UNIQUE ({idxs}){on_conflict}"
    elif isinstance(constraint, sql.ForeignKey):
        cols = ", ".join(f'"{col}"' for col in constraint.columns)
        return f"{name}FOREIGN KEY ({cols}) " + _generate_foreign_key_clause(constraint)
    else:
        expr = _generate_tokens(constraint.expr)
        return f"{name}CHECK ({expr})"


def _generate_foreign_key_clause(constraint: sql.ForeignKey, /) -> str:
    foreign_table = _generate_qualified_name(constraint.foreign_table)
    referred_columns = (
        ("(" + ", ".join(f'"{col}"' for col in constraint.referred_columns) + ")")
        if constraint.referred_columns is not None
        else ""
    )
    on_update = _generate_on_update_delete(constraint.on_update, True)
    on_delete = _generate_on_update_delete(constraint.on_delete, False)
    match = f" MATCH {constraint.match.name}" if constraint.match is not None else ""
    enforcement = _generate_constraint_enforcement(constraint.enforcement)
    return (
        f"REFERENCES {foreign_table}{referred_columns}"
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
        collation = f" COLLATE {indexed.collation.name}"
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


def _generate_tokens(expr: Iterable[tok.Token], /) -> str:
    return " ".join(_generate_tok(tk) for tk in expr)


def _generate_tok(tk: tok.Token, /) -> str:
    if bool(tk.kind & tok.TokenKind.DELIMITED_ID):
        return f'"{tk.val}"'
    elif bool(tk.kind & tok.TokenKind.STR):
        return f"'{tk.val}'"
    elif bool(tk.kind & tok.TokenKind.BLOB):
        return f"X'{tk.val}'"
    elif bool(tk.kind & tok.TokenKind.BINARY):
        return f"B'{tk.val}'"
    elif bool(tk.kind & tok.TokenKind.HEX):
        return f"0x{tk.val}"
    elif bool(tk.kind & tok.TokenKind.NUMERIC):
        return f"{tk.val}"
    elif bool(tk.kind & tok.TokenKind.TRIVIA):
        return ""
    else:
        return tk.val
