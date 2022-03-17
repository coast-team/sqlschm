from typing import Iterable
from sqlschm import sql, tok, lexer

Lex = lexer.ItemCursor[tok.Token]


class ParserError(Exception):
    pass


# sentinel to mark the end of a token stream
_EOF_TOKEN: tok.Token = tok.Token(tok.TokenKind.UNKNOWN, "")


def parse_schema(src: Iterable[str], /) -> sql.Schema:
    non_trivia_tokens = filter(tok.is_not_trivia, lexer.tokens(src))
    l = lexer.ItemCursor(non_trivia_tokens, _EOF_TOKEN)
    tables: list[sql.Table] = []
    while l.item is not _EOF_TOKEN:
        tables.append(_parse_create_table(l))
    return sql.Schema(tables=tuple(tables))


def _parse_create_table(l: Lex, /) -> sql.Table:
    if_not_exists = False
    or_replace = False
    temporary = False
    _expect(l, tok.CREATE)
    if l.item is tok.OR:
        l.forth()
        _expect(l, tok.REPLACE)
        or_replace = True
    if l.item is tok.TEMPORARY or l.item is tok.TEMP:
        l.forth()
        temporary = True
    _expect(l, tok.TABLE)
    if l.item is tok.IF:
        l.forth()
        _expect(l, tok.NOT)
        _expect(l, tok.EXISTS)
        if_not_exists = True
    table_name = _parse_qualified_name(l)
    if l.item is tok.AS or l.item is tok.LIKE:
        # FIXME: support this case?
        raise ParserError(f"'CREATE TABLE {l.item.val}' is not supported.")
    _expect(l, tok.L_PAREN)
    columns: list[sql.Column] = []
    constraints: list[sql.Constraint] = []
    if l.item is not tok.R_PAREN:
        (column, col_constraint) = _parse_column_def(l)
        columns.append(column)
        constraints += col_constraint
        while l.item is tok.COMMA and l.next_item.kind is not tok.TokenKind.KEYWORD:
            l.forth()
            (column, col_constraint) = _parse_column_def(l)
            columns.append(column)
            constraints += col_constraint
        while l.item is tok.COMMA:
            l.forth()
            constraint = _parse_constraint(l, None)
            if constraint is not None:
                constraints.append(constraint)
        _expect(l, tok.R_PAREN)
    options = _parse_table_options(l)
    if l.item is tok.SELECT:
        # consume SELECT expression
        while l.item is not tok.SEMICOLON:
            l.forth()
    _expect(l, tok.SEMICOLON)
    return sql.Table(
        name=table_name,
        if_not_exists=if_not_exists,
        or_replace=or_replace,
        temporary=temporary,
        columns=columns,
        constraints=constraints,
        options=options,
    )


def _parse_column_def(l: Lex, /) -> tuple[sql.Column, list[sql.Constraint]]:
    colname = _parse_name(l)
    coltype = _parse_type(l)
    not_null = False
    autoincrement = False
    generated = False
    default = None
    collation = None
    col_constraints: list[sql.Constraint] = []
    while l.item is not tok.COMMA and l.item is not tok.R_PAREN:
        if l.item is tok.NULL:
            l.forth()
        elif l.item is tok.NOT:
            l.forth()
            _expect(l, tok.NULL)
            _parse_on_conflict(l)
            not_null = True
        elif l.item is tok.DEFAULT:
            default = _parse_default(l)
        elif l.item is tok.COLLATE:
            l.forth()
            collation = _parse_name(l)
        elif l.item is tok.GENERATED or l.item is tok.AS:
            if l.item is tok.GENERATED:
                l.forth()
                if l.item is tok.ALWAYS:
                    l.forth()
                elif l.item is tok.BY and l.next_item is tok.DEFAULT:
                    l.forth()
                    l.forth()
                else:
                    raise ParserError("'ALWAYS' or 'BY DEFAULT' is expected.")
                _expect(l, tok.AS)
                if l.item is tok.IDENTITY:
                    l.forth()
            else:
                l.forth()
            skip_parens(l)
            if bool(l.item.kind & tok.TokenKind.ID) and l.item.val.upper() in [
                "PERSISTENT",
                "STORED",
                "VIRTUAL",
            ]:
                l.forth()
            generated = True
        elif l.item is tok.AUTOINCREMENT or l.item is tok.AUTO_INCREMENT:
            l.forth()
            autoincrement = True
        else:
            constraint = _parse_constraint(l, colname)
            if constraint is not None:
                col_constraints.append(constraint)
    return (
        sql.Column(
            name=colname,
            type=coltype,
            not_null=not_null,
            autoincrement=autoincrement,
            generated=generated,
            default=default,
            collation=collation,
        ),
        col_constraints,
    )


def _parse_default(l: Lex, /) -> sql.Default:
    _expect(l, tok.DEFAULT)
    if bool(l.item.kind & tok.TokenKind.LITERAL):
        l.forth()
    elif l.item is tok.NUM_PLUS or l.item is tok.NUM_MINUS:
        l.forth()
        _parse_int(l)
    elif bool(l.item.kind & tok.TokenKind.ID) and l.next_item is tok.L_PAREN:
        # function call
        l.forth()
        skip_parens(l)
    elif l.item is tok.L_PAREN:
        skip_parens(l)
    else:
        raise ParserError(f"'{l.item.val}' is not a supported DEFAULT value.")
    return sql.Default()


def _parse_table_options(l: Lex, /) -> sql.TableOptions:
    strict = False
    without_rowid = False
    while True:
        if l.item is tok.STRICT:
            l.forth()
            strict = True
        elif l.item is tok.WITHOUT:
            l.forth()
            _expect(l, tok.ROWID)
            without_rowid = True
        if l.item is tok.COMMA:
            l.forth()
        else:
            break
    return sql.TableOptions(strict=strict, without_rowid=without_rowid)


def _parse_type(l: Lex, /) -> sql.Type:
    # see https://www.sqlite.org/datatype3.html
    # TODO: while it is not a keyword, a comma, or a rparen -> it is the type!
    type_name = ""
    type_params: list[int] = []
    while bool(l.item.kind & tok.TokenKind.NON_KW_ID):
        type_name += l.item.val.upper() + " "
        l.forth()
    type_name = type_name.rstrip()
    if type_name != "":
        if l.item is tok.L_PAREN:
            l.forth()
            type_params.append(_parse_int(l))
            if l.item is tok.COMMA:
                type_params.append(_parse_int(l))
            _expect(l, tok.R_PAREN)
    return sql.Type(name=type_name, params=tuple(type_params))


def _parse_constraint(l: Lex, col_name: str | None, /) -> sql.Constraint | None:
    columns = tuple() if col_name is None else tuple([col_name])
    name = None
    if l.item is tok.CONSTRAINT:
        name = _parse_name(l)  # skip name
    if l.item is tok.PRIMARY:
        l.forth()
        _expect(l, tok.KEY)
        if l.item is tok.ASC or l.item is tok.DESC:
            l.forth()
        if col_name is None:
            columns = _parse_parens_names(l)
        on_conflict = _parse_on_conflict(l)
        return sql.Uniqueness(
            name=name,
            columns=columns,
            is_primary=True,
            on_conflict=on_conflict,
        )
    elif l.item is tok.UNIQUE:
        l.forth()
        if col_name is None:
            columns = _parse_parens_names(l)
        on_conflict = _parse_on_conflict(l)
        return sql.Uniqueness(name=name, columns=columns, on_conflict=on_conflict)
    elif l.item is tok.CHECK:
        l.forth()
        skip_parens(l)
        return None
    elif col_name is None and l.item is tok.FOREIGN:
        l.forth()
        _expect(l, tok.KEY)
        columns = _parse_parens_names(l)
        return _parse_foreign_key_clause(l, columns, name)
    elif l.item is tok.REFERENCES:
        return _parse_foreign_key_clause(l, columns, name)
    else:
        raise ParserError(f"'{l.item.val}' cannot start a constraint")


def _parse_parens_names(l: Lex, /) -> tuple[str, ...]:
    _expect(l, tok.L_PAREN)
    names = [_parse_name(l)]
    while l.item is tok.COMMA:
        l.forth()
        names.append(_parse_name(l))
    _expect(l, tok.R_PAREN)
    return tuple(names)


def _parse_foreign_key_clause(
    l: Lex, columns: tuple[str, ...], name: str | None, /
) -> sql.ForeignKey:
    _expect(l, tok.REFERENCES)
    foreign_table = _parse_qualified_name(l)
    referred_columns: tuple[str, ...] | None = None
    on_delete = sql.OnUpdateDelete.NO_ACTION
    on_update = sql.OnUpdateDelete.NO_ACTION
    not_deferrable = False
    initially_deferred = False
    if l.item is tok.L_PAREN:
        referred_columns = _parse_parens_names(l)
    while l.item is tok.ON or l.item is tok.MATCH:
        if l.item is tok.ON:
            l.forth()
            if l.item is tok.DELETE:
                l.forth()
                on_delete = _parse_on_updatedelete_action(l)
            elif l.item is tok.UPDATE:
                l.forth()
                on_update = _parse_on_updatedelete_action(l)
            else:
                raise ParserError("'ON DELETE' or 'ON UPDATE' is expected")
        elif l.item is tok.MATCH:
            l.forth()
            l.forth()  # consume FULL or PARTIAL or SIMPLE
    if l.item is tok.NOT and l.next_item is tok.DEFERRABLE:
        l.forth()
        not_deferrable = True
    if l.item is tok.DEFERRABLE:
        l.forth()
        if l.item is tok.INITIALLY:
            l.forth()
            if not (l.item is tok.DEFERRED or l.item is tok.IMMEDIATE):
                raise ParserError(f"'{l.item.val}' is not a valid dererrable state")
            initially_deferred = l.item.val is tok.DEFERRED
            l.forth()
    return sql.ForeignKey(
        name=name,
        columns=columns,
        foreign_table=foreign_table,
        referred_columns=referred_columns,
        on_delete=on_delete,
        on_update=on_update,
        enforcement=sql.ConstraintEnforcement(
            initially_deferred=initially_deferred, not_deferrable=not_deferrable
        ),
    )


def _parse_on_updatedelete_action(l: Lex, /) -> sql.OnUpdateDelete:
    if l.item is tok.CASCADE:
        l.forth()
        return sql.OnUpdateDelete.CASCADE
    elif l.item is tok.NO and l.next_item is tok.ACTION:
        l.forth()
        l.forth()
        return sql.OnUpdateDelete.NO_ACTION
    elif l.item is tok.SET and l.next_item is tok.NULL:
        l.forth()
        l.forth()
        return sql.OnUpdateDelete.SET_NULL
    elif l.item is tok.SET and l.next_item is tok.DEFAULT:
        l.forth()
        l.forth()
        return sql.OnUpdateDelete.SET_DEFAULT
    elif l.item is tok.RESTRICT:
        l.forth()
        return sql.OnUpdateDelete.RESTRICT
    else:
        raise ParserError("'Invalid ON DELETE/UPDATE action")


def _parse_on_conflict(l: Lex, /) -> sql.OnConflict:
    if l.item is tok.ON:
        l.forth()
        _expect(l, tok.CONFLICT)
        if l.item.val not in sql.ON_CONFLICT:
            raise ParserError(f"'{l.item.val}' is not a valid ON CONFLICT ACTION")
        result = sql.OnConflict[l.item.val]
        l.forth()
        return result
    else:
        return sql.OnConflict.ABORT  # Default


def _parse_int(l: Lex, /) -> int:
    if l.item is not tok.TokenKind.INT:
        raise ParserError("an integer is expected.")
    result = int(l.item)
    l.forth()
    return result


def _parse_qualified_name(l: Lex, /) -> sql.QualifiedName:
    names = [_parse_name(l)]
    while l.item is tok.DOT:
        l.forth()
        names.append(_parse_name(l))
    names.reverse()
    return tuple(names)


def _parse_name(l: Lex, /) -> str:
    if not bool(l.item.kind & tok.TokenKind.ID):
        raise ParserError(f"an identifier is expected.")
    result = l.item.val
    l.forth()
    return result


def skip_expr(l: Lex, /) -> None:
    if l.item is tok.L_PAREN:
        skip_parens(l)
    else:
        if l.item is tok.INTERNED["+"] or l.item is tok.INTERNED["-"]:
            l.forth()
        _skip(l, tok.TokenKind.LITERAL)


def skip_parens(l: Lex, /) -> None:
    _expect(l, tok.L_PAREN)
    count = 0
    while l.item is not tok.R_PAREN or count > 0:
        if l.item is tok.L_PAREN:
            count += 1
        elif l.item is tok.R_PAREN:
            count -= 1
        l.forth()
    l.forth()


def _expect(l: Lex, tk: tok.Token, /) -> None:
    if l.item is not tk:
        raise ParserError(f"'{tk.val}' is expected. Got '{l.item.val}'.")
    l.forth()


def _skip(l: Lex, kind: tok.TokenKind, /) -> None:
    if l.item.kind is kind:
        raise ParserError(f"a {kind.name} is expected")
    l.forth()
