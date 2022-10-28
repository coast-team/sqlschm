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
    tables: list[sql.SchemaItem] = []
    while l.item is not _EOF_TOKEN:
        if l.item is tok.SEMICOLON:
            l.forth()
            continue
        tables.append(_parse_create_statement(l))
    return sql.Schema(items=tuple(tables))


def _parse_create_statement(l: Lex, /) -> sql.Table | sql.Index:
    if l.item is tok.CREATE and (l.next_item is tok.UNIQUE or l.next_item is tok.INDEX):
        return _parse_create_index(l)
    return _parse_create_table(l)


def _parse_create_index(l: Lex, /) -> sql.Index:
    if_not_exists = False
    unique = False
    _expect(l, tok.CREATE)
    if l.item is tok.UNIQUE:
        l.forth()
        unique = True
    _expect(l, tok.INDEX)
    if l.item is tok.IF:
        l.forth()
        _expect(l, tok.NOT)
        _expect(l, tok.EXISTS)
        if_not_exists = True
    index_name = _parse_qualified_name(l)
    _expect(l, tok.ON)
    table_name = _parse_name(l)
    indexed = _parse_indexed_names(l)
    expr = None
    if l.item is tok.WHERE:
        l.forth()
        expr = _tokens_until_semicolon(l)
    _expect(l, tok.SEMICOLON)
    return sql.Index(
        name=index_name,
        table=table_name,
        indexed=indexed,
        where=expr,
        if_not_exists=if_not_exists,
        unique=unique,
    )


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
    constraints: list[sql.TableConstraint] = []
    if l.item is not tok.R_PAREN:
        columns.append(_parse_column_def(l))
        while l.item is tok.COMMA and l.next_item.kind is not tok.TokenKind.KEYWORD:
            l.forth()
            columns.append(_parse_column_def(l))
        while l.item is tok.COMMA:
            l.forth()
            constraints.append(_parse_table_constraint(l))
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
        columns=tuple(columns),
        constraints=tuple(constraints),
        options=options,
    )


def _parse_column_def(l: Lex, /) -> sql.Column:
    colname = _parse_name(l)
    coltype = _parse_type(l)
    constraints: list[sql.ColumnConstraint] = []
    while l.item is not tok.COMMA and l.item is not tok.R_PAREN:
        constraints.append(_parse_col_constraint(l, colname))
    return sql.Column(name=colname, type=coltype, constraints=tuple(constraints))


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


def _parse_table_constraint(l: Lex, /) -> sql.TableConstraint:
    name = None
    if l.item is tok.CONSTRAINT:
        l.forth()
        name = _parse_name(l)
    if l.item is tok.PRIMARY or l.item is tok.UNIQUE:
        is_primary = l.item is tok.PRIMARY
        l.forth()
        if is_primary:
            _expect(l, tok.KEY)
        return sql.Uniqueness(
            name=name,
            is_table_constraint=True,
            indexed=_parse_indexed_names(l),
            is_primary=is_primary,
            on_conflict=_parse_on_conflict(l),
        )
    elif l.item is tok.FOREIGN:
        l.forth()
        _expect(l, tok.KEY)
        columns = _parse_parens_names(l)
        return _parse_foreign_key_clause(l, columns, name, is_table_constraint=True)
    elif l.item is tok.CHECK:
        l.forth()
        expr = tokens_in_parens(l)
        return sql.Check(name=name, is_table_constraint=True, expr=expr)
    else:
        raise ParserError(f"'{l.item.val}' cannot start a table constraint")


def _parse_col_constraint(l: Lex, col_name: str, /) -> sql.ColumnConstraint:
    name = None
    if l.item is tok.CONSTRAINT:
        l.forth()
        name = _parse_name(l)
    if l.item is tok.PRIMARY or l.item is tok.UNIQUE:
        is_primary = l.item is tok.PRIMARY
        l.forth()
        if is_primary:
            _expect(l, tok.KEY)
        sorting = _parse_optional_sorting(l)
        indexed = (sql.Indexed(column=col_name, sorting=sorting),)
        on_conflict = _parse_on_conflict(l)
        autoincrement = l.item is tok.AUTOINCREMENT or l.item is tok.AUTO_INCREMENT
        if autoincrement:
            l.forth()
        return sql.Uniqueness(
            name=name,
            indexed=indexed,
            is_primary=is_primary,
            autoincrement=autoincrement,
            on_conflict=on_conflict,
        )
    elif l.item is tok.CHECK:
        l.forth()
        expr = tokens_in_parens(l)
        return sql.Check(name=name, expr=expr)
    elif l.item is tok.REFERENCES:
        return _parse_foreign_key_clause(l, (col_name,), name)
    elif l.item is tok.NOT:
        l.forth()
        _expect(l, tok.NULL)
        return sql.NotNull(name=name, on_conflict=_parse_on_conflict(l))
    elif l.item is tok.DEFAULT:
        l.forth()
        return sql.Default(name=name, expr=_parse_expr(l))
    elif l.item is tok.COLLATE:
        l.forth()
        return sql.Collation(name=name, value=_parse_name(l))
    elif l.item is tok.GENERATED or l.item is tok.AS:
        if l.item is tok.GENERATED and l.next_item is tok.ALWAYS:
            l.forth()
            l.forth()
        elif l.item is tok.GENERATED and l.next_item is tok.BY:
            l.forth()
            l.forth()
            _expect(l, tok.DEFAULT)
        _expect(l, tok.AS)
        if l.item is tok.IDENTITY:
            l.forth()
        expr = tokens_in_parens(l)
        kind = None
        tok_val = l.item.val.upper()
        if bool(l.item.kind & tok.TokenKind.ID) and tok_val in sql.GENERATED_KIND:
            kind = sql.GeneratedKind[tok_val]
            l.forth()
        return sql.Generated(name=name, expr=expr, kind=kind)
    else:
        raise ParserError(f"'{l.item.val}' cannot start a column constraint")


def _parse_indexed_names(l: Lex, /) -> tuple[sql.Indexed, ...]:
    _expect(l, tok.L_PAREN)
    result = [_parse_indexed_name(l)]
    while l.item is tok.COMMA:
        l.forth()
        result.append(_parse_indexed_name(l))
    _expect(l, tok.R_PAREN)
    return tuple(result)


def _parse_indexed_name(l: Lex, /) -> sql.Indexed:
    column = _parse_name(l)
    collation = None
    if l.item is tok.COLLATE:
        l.forth()
        collation = sql.Collation(value=_parse_name(l))
    sorting = _parse_optional_sorting(l)
    return sql.Indexed(column=column, collation=collation, sorting=sorting)


def _parse_optional_sorting(l: Lex, /) -> sql.Sorting | None:
    if l.item is tok.ASC:
        l.forth()
        return sql.Sorting.ASC
    elif l.item is tok.DESC:
        l.forth()
        return sql.Sorting.DESC
    return None


def _parse_expr(l: Lex, /) -> tuple[tok.Token, ...]:
    result: list[tok.Token] = []
    if bool(l.item.kind & tok.TokenKind.LITERAL):
        result.append(l.item)
        l.forth()
    elif l.item is tok.NUM_PLUS or l.item is tok.NUM_MINUS:
        result += [l.item, l.next_item]
        l.forth()
        _parse_int(l)  # ensure it is an integer
    elif bool(l.item.kind & tok.TokenKind.ID) and l.next_item is tok.L_PAREN:
        # function call
        result.append(l.item)
        l.forth()
        result.append(tok.L_PAREN)
        result += tokens_in_parens(l)
        result.append(tok.R_PAREN)
    elif l.item is tok.L_PAREN:
        result += tokens_in_parens(l)
    else:
        raise ParserError(f"'{l.item.val}' is not a supported DEFAULT value.")
    return tuple(result)


def _parse_parens_names(l: Lex, /) -> tuple[str, ...]:
    _expect(l, tok.L_PAREN)
    result = [_parse_name(l)]
    while l.item is tok.COMMA:
        l.forth()
        result.append(_parse_name(l))
    _expect(l, tok.R_PAREN)
    return tuple(result)


def _parse_foreign_key_clause(
    l: Lex,
    columns: tuple[str, ...],
    name: str | None,
    /,
    *,
    is_table_constraint: bool = False,
) -> sql.ForeignKey:
    _expect(l, tok.REFERENCES)
    foreign_table = _parse_qualified_name(l)
    referred_columns: tuple[str, ...] | None = None
    on_delete: sql.OnUpdateDelete | None = None
    on_update: sql.OnUpdateDelete | None = None
    match: sql.Match | None = None
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
            match_name = _parse_name(l).upper()
            if match_name not in sql.MATCH:
                raise ParserError("invalid MATCH name")
            match = sql.Match[match_name]
    enforcement = _parse_constraint_enforcement(l)
    return sql.ForeignKey(
        name=name,
        columns=columns,
        foreign_table=foreign_table,
        referred_columns=referred_columns,
        is_table_constraint=is_table_constraint,
        on_delete=on_delete,
        on_update=on_update,
        match=match,
        enforcement=enforcement,
    )


def _parse_constraint_enforcement(l: Lex, /) -> sql.ConstraintEnforcement | None:
    initially = _parse_constraint_enforcement_time(l)
    not_deferrable = None
    if l.item is tok.NOT and l.next_item is tok.DEFERRABLE:
        l.forth()
        not_deferrable = True
    if l.item is tok.DEFERRABLE:
        l.forth()
        not_deferrable = False
        if initially is None:
            initially = _parse_constraint_enforcement_time(l)
    if not_deferrable is not None:
        return sql.ConstraintEnforcement(
            initially=initially, not_deferrable=not_deferrable
        )
    return None


def _parse_constraint_enforcement_time(
    l: Lex, /
) -> sql.ConstraintEnforcementTime | None:
    if l.item is tok.INITIALLY:
        l.forth()
        if l.item is tok.DEFERRED:
            l.forth()
            return sql.ConstraintEnforcementTime.DEFERRED
        elif l.item is tok.IMMEDIATE:
            l.forth()
            return sql.ConstraintEnforcementTime.IMMEDIATE
        else:
            raise ParserError(f"'{l.item.val}' is not a valid enforcement time")
    return None


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


def _parse_on_conflict(l: Lex, /) -> sql.OnConflict | None:
    if l.item is tok.ON:
        l.forth()
        _expect(l, tok.CONFLICT)
        if l.item.val not in sql.ON_CONFLICT:
            raise ParserError(f"'{l.item.val}' is not a valid ON CONFLICT ACTION")
        result = sql.OnConflict[l.item.val]
        l.forth()
        return result
    else:
        return None


def _parse_int(l: Lex, /) -> int:
    if l.item.kind is not tok.TokenKind.INT:
        raise ParserError("an integer is expected.")
    result = int(l.item.val)
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


def tokens_in_parens(l: Lex, /) -> tuple[tok.Token, ...]:
    result: list[tok.Token] = []
    _expect(l, tok.L_PAREN)
    count = 0
    while l.item is not tok.R_PAREN or count > 0:
        result.append(l.item)
        if l.item is tok.L_PAREN:
            count += 1
        elif l.item is tok.R_PAREN:
            count -= 1
        l.forth()
    l.forth()
    return tuple(result)


def _tokens_until_semicolon(l: Lex, /) -> tuple[tok.Token, ...]:
    result: list[tok.Token] = []
    while l.item is not tok.SEMICOLON:
        result.append(l.item)
        l.forth()
    return tuple(result)


def _expect(l: Lex, tk: tok.Token, /) -> None:
    if l.item is not tk:
        raise ParserError(f"'{tk.val}' is expected. Got '{l.item.val}'.")
    l.forth()


def _skip(l: Lex, kind: tok.TokenKind, /) -> None:
    if l.item.kind is kind:
        raise ParserError(f"a {kind.name} is expected")
    l.forth()
