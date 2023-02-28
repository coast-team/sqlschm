from sqlschm import lexer, tok
from sqlschm.tok import Token, TokenKind


def test_newline() -> None:
    tks = list(lexer.tokens("\n"))
    assert tks == [tok.NEWLINE]


def test_non_newline_spaces() -> None:
    tks = list(lexer.tokens("  \t"))
    assert tks == [tok.INTERNED[" "], tok.INTERNED[" "], tok.INTERNED["\t"]]


def test_spaces() -> None:
    tks = list(lexer.tokens("\n \n\t"))
    assert tks == [
        tok.NEWLINE,
        tok.INTERNED[" "],
        tok.NEWLINE,
        tok.INTERNED["\t"],
    ]


def test_int() -> None:
    for item in ["42", "042"]:
        tks = list(lexer.tokens(item))
        assert tks == [Token(TokenKind.INT, item)]


def test_hex() -> None:
    tks = list(lexer.tokens("0x7f"))
    assert tks == [Token(TokenKind.HEX, "7f")]


def test_float() -> None:
    for item in ["1.0", "0.", ".0", "0.e5", "0.e-5", "0.e+5", ".0e5", "1e-3"]:
        tks = list(lexer.tokens(item))
        assert tks == [Token(TokenKind.FLOAT, item)]


def test_binary() -> None:
    tks = list(lexer.tokens("b'010'"))
    assert tks == [Token(TokenKind.BINARY, "010")]


def test_blob() -> None:
    tks = list(lexer.tokens("x'ae5'"))
    assert tks == [Token(TokenKind.BLOB, "ae5")]

    tks = list(lexer.tokens('x"ae5"'))
    assert tks == [Token(TokenKind.BLOB, "ae5")]


def test_raw_id() -> None:
    tks = list(lexer.tokens("id"))
    assert tks == [Token(TokenKind.RAW_ID, "id")]


def test_enclosed_id() -> None:
    tks = list(lexer.tokens("[create]"))
    assert tks == [Token(TokenKind.NON_STD_DELIMITED_ID, "create")]

    tks = list(lexer.tokens("`create`"))
    assert tks == [Token(TokenKind.NON_STD_DELIMITED_ID, "create")]


def test_interned() -> None:
    for val, token in tok.INTERNED.items():
        tks = list(lexer.tokens(val))
        assert tks == [token]


def test_str() -> None:
    tks = list(lexer.tokens("'a string'"))
    assert tks == [Token(TokenKind.STD_STR, "a string")]


def test_delimited_id() -> None:
    tks = list(lexer.tokens('"a id"'))
    assert tks == [Token(TokenKind.STD_DELIMITED_ID, "a id")]

    tks = list(lexer.tokens('"""quoted"""'))
    assert tks == [Token(TokenKind.STD_DELIMITED_ID, '"quoted"')]

    tks = list(lexer.tokens('"a ""quoted"" id"'))
    assert tks == [Token(TokenKind.STD_DELIMITED_ID, 'a "quoted" id')]


def test_single_line_comment() -> None:
    tks = list(lexer.tokens("-- a comment\n"))
    assert tks == [Token(TokenKind.SINGLE_LINE_COMMENT, " a comment")]


def test_multi_line_comment() -> None:
    tks = list(lexer.tokens("/* a comment\n\n on several lines */"))
    assert tks == [
        Token(TokenKind.MULTI_LINE_COMMENT, " a comment\n\n on several lines ")
    ]


def test_identifier() -> None:
    tks = list(lexer.tokens("table_1"))
    assert tks == [Token(TokenKind.RAW_ID, "table_1")]


def test_unknown() -> None:
    tks = list(lexer.tokens("@"))
    assert tks == [Token(TokenKind.UNKNOWN, "@")]

    tks = list(lexer.tokens("'an unterminated str"))
    assert tks == [Token(TokenKind.UNKNOWN, "'an unterminated str")]

    tks = list(lexer.tokens("/* an unterminated comment"))
    assert tks == [Token(TokenKind.UNKNOWN, "/* an unterminated comment")]


def test_complex() -> None:
    schm = "CREATE TABLE table_name(\ncol int DEFAULT 1-- comment\n);"
    tks = list(lexer.tokens(schm))
    assert tks == [
        tok.CREATE,
        tok.INTERNED[" "],
        tok.TABLE,
        tok.INTERNED[" "],
        Token(TokenKind.RAW_ID, "table_name"),
        tok.L_PAREN,
        tok.NEWLINE,
        Token(TokenKind.RAW_ID, "col"),
        tok.INTERNED[" "],
        Token(TokenKind.RAW_ID, "int"),
        tok.INTERNED[" "],
        tok.DEFAULT,
        tok.INTERNED[" "],
        Token(TokenKind.INT, "1"),
        Token(TokenKind.SINGLE_LINE_COMMENT, " comment"),
        tok.R_PAREN,
        tok.SEMICOLON,
    ]
