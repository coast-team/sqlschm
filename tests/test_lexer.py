from sqlschm import lexer, tok
from sqlschm.tok import Token, TokenKind


def test_newline():
    tks = list(lexer.tokens("\n"))
    assert tks == [tok.NEWLINE]


def test_non_newline_spaces():
    tks = list(lexer.tokens("  \t"))
    assert tks == [tok.INTERNED[" "], tok.INTERNED[" "], tok.INTERNED["\t"]]


def test_spaces():
    tks = list(lexer.tokens("\n \n\t"))
    assert tks == [
        tok.NEWLINE,
        tok.INTERNED[" "],
        tok.NEWLINE,
        tok.INTERNED["\t"],
    ]


def test_int():
    for x in ["42", "042"]:
        tks = list(lexer.tokens(x))
        assert tks == [Token(TokenKind.INT, x)]


def test_hex():
    tks = list(lexer.tokens("0x7f"))
    assert tks == [Token(TokenKind.HEX, "7f")]


def test_float():
    for x in ["1.0", "0.", ".0", "0.e5", "0.e-5", "0.e+5", ".0e5", "1e-3"]:
        tks = list(lexer.tokens(x))
        assert tks == [Token(TokenKind.FLOAT, x)]


def test_binary():
    tks = list(lexer.tokens("b'010'"))
    assert tks == [Token(TokenKind.BINARY, "010")]


def test_blob():
    tks = list(lexer.tokens("x'ae5'"))
    assert tks == [Token(TokenKind.BLOB, "ae5")]

    tks = list(lexer.tokens('x"ae5"'))
    assert tks == [Token(TokenKind.BLOB, "ae5")]


def test_raw_id():
    tks = list(lexer.tokens("id"))
    assert tks == [Token(TokenKind.RAW_ID, "id")]


def test_enclosed_id():
    tks = list(lexer.tokens("[create]"))
    assert tks == [Token(TokenKind.NON_STD_DELIMITED_ID, "create")]

    tks = list(lexer.tokens("`create`"))
    assert tks == [Token(TokenKind.NON_STD_DELIMITED_ID, "create")]


def test_interned():
    for x in tok.INTERNED:
        tks = list(lexer.tokens(x))
        assert tks == [tok.INTERNED[x]]


def test_str():
    tks = list(lexer.tokens("'a string'"))
    assert tks == [Token(TokenKind.STD_STR, "a string")]


def test_delimited_id():
    tks = list(lexer.tokens('"a id"'))
    assert tks == [Token(TokenKind.STD_DELIMITED_ID, "a id")]

    tks = list(lexer.tokens('"""quoted"""'))
    assert tks == [Token(TokenKind.STD_DELIMITED_ID, '"quoted"')]

    tks = list(lexer.tokens('"a ""quoted"" id"'))
    assert tks == [Token(TokenKind.STD_DELIMITED_ID, 'a "quoted" id')]


def test_single_line_comment():
    tks = list(lexer.tokens("-- a comment\n"))
    assert tks == [Token(TokenKind.SINGLE_LINE_COMMENT, " a comment")]


def test_multi_line_comment():
    tks = list(lexer.tokens("/* a comment\n\n on several lines */"))
    assert tks == [
        Token(TokenKind.MULTI_LINE_COMMENT, " a comment\n\n on several lines ")
    ]


def test_identifier():
    tks = list(lexer.tokens("table_1"))
    assert tks == [Token(TokenKind.RAW_ID, "table_1")]


def test_unknown():
    tks = list(lexer.tokens("@"))
    assert tks == [Token(TokenKind.UNKNOWN, "@")]

    tks = list(lexer.tokens("'an unterminated str"))
    assert tks == [Token(TokenKind.UNKNOWN, "'an unterminated str")]

    tks = list(lexer.tokens("/* an unterminated comment"))
    assert tks == [Token(TokenKind.UNKNOWN, "/* an unterminated comment")]


def test_complex():
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
