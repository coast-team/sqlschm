from dataclasses import dataclass
from enum import Flag, unique, auto


@unique
class TokenKind(Flag):
    KEYWORD = auto()

    RAW_ID = auto()  # id
    STD_DELIMITED_ID = auto()  # "id"

    NON_STD_DELIMITED_ID = auto()  # `id` or [id]
    DELIMITED_ID = STD_DELIMITED_ID | NON_STD_DELIMITED_ID

    STD_STR = auto()  # 'a string'
    STR = STD_STR | STD_DELIMITED_ID  # 'a string' or "a string"

    NON_KW_ID = RAW_ID | DELIMITED_ID | STD_STR
    ID = NON_KW_ID | KEYWORD

    PREDEF_LITERAL = auto()
    KEYWORD_LITERAL = KEYWORD | PREDEF_LITERAL  # NULL, CURRENT_*
    RAW_ID_LITERAL = RAW_ID | PREDEF_LITERAL  # TRUE, FALSE

    BLOB = auto()
    BINARY = auto()
    FLOAT = auto()  # .5e+6
    HEX = auto()  # 0x5A
    INT = auto()  # 123
    NUMERIC = FLOAT | HEX | INT
    LITERAL = BLOB | BINARY | NUMERIC | STR | PREDEF_LITERAL

    BIN_OP = auto()
    CMP_OP = auto()
    NUM_OP = auto()
    STR_OP = auto()
    OPERATOR = BIN_OP | CMP_OP | NUM_OP | STR_OP

    PUNCTUATION = auto()

    SINGLE_LINE_COMMENT = auto()  # -- or #<space>
    MULTI_LINE_COMMENT = auto()  # /* */
    COMMENT = SINGLE_LINE_COMMENT | MULTI_LINE_COMMENT

    WHITESPACE = auto()
    TRIVIA = WHITESPACE | COMMENT

    UNKNOWN = auto()
    UNKNOWN_OR_TRIVIA = UNKNOWN | TRIVIA


@dataclass(frozen=True, slots=True)
class Token:
    kind: TokenKind
    val: str


def is_not_trivia(tk: Token, /) -> bool:
    return not bool(tk.kind & TokenKind.TRIVIA)


def like(a: Token, b: Token, /) -> bool:
    return bool(a.kind & b.kind) and a.val == b.val


# Spaces
NEWLINE: Token = Token(TokenKind.WHITESPACE, "\n")

# *
WILDCARD: Token = Token(TokenKind.NUM_OP, "*")

# Binary operators
BIN_NEG: Token = Token(TokenKind.BIN_OP, "~")
BIN_AND: Token = Token(TokenKind.BIN_OP, "&")
BIN_OR: Token = Token(TokenKind.BIN_OP, "|")
BIN_LSHIFT: Token = Token(TokenKind.BIN_OP, "<<")
BIN_RSHIFT: Token = Token(TokenKind.BIN_OP, ">>")

# Numeric operators
NUM_PLUS: Token = Token(TokenKind.NUM_OP, "+")
NUM_MINUS: Token = Token(TokenKind.NUM_OP, "-")
NUM_DIV: Token = Token(TokenKind.NUM_OP, "/")
NUM_MOD: Token = Token(TokenKind.NUM_OP, "%")
NUM_EXP: Token = Token(TokenKind.NUM_OP, "^")

# Comparison operators
CMP_EQ: Token = Token(TokenKind.CMP_OP, "=")
CMP_EQ2: Token = Token(TokenKind.CMP_OP, "==")
CMP_GEQ: Token = Token(TokenKind.CMP_OP, ">=")
CMP_GEQ2: Token = Token(TokenKind.CMP_OP, "!>")
CMP_GT: Token = Token(TokenKind.CMP_OP, ">")
CMP_LEQ: Token = Token(TokenKind.CMP_OP, "<=")
CMP_LEQ2: Token = Token(TokenKind.CMP_OP, "!<")
CMP_LT: Token = Token(TokenKind.CMP_OP, "<")
CMP_NEQ: Token = Token(TokenKind.CMP_OP, "<>")
CMP_NEQ2: Token = Token(TokenKind.CMP_OP, "!=")

# String operators
STR_CONCAT: Token = Token(TokenKind.STR_OP, "||")

# Punctuation
DOT: Token = Token(TokenKind.PUNCTUATION, ".")
COMMA: Token = Token(TokenKind.PUNCTUATION, ",")
COLON: Token = Token(TokenKind.PUNCTUATION, ":")
DOUBLE_COLON: Token = Token(TokenKind.PUNCTUATION, "::")
SEMICOLON: Token = Token(TokenKind.PUNCTUATION, ";")
L_PAREN: Token = Token(TokenKind.PUNCTUATION, "(")
R_PAREN: Token = Token(TokenKind.PUNCTUATION, ")")

# Known raw identifiers
ROWID: Token = Token(TokenKind.RAW_ID, "ROWID")
STRICT: Token = Token(TokenKind.RAW_ID, "STRICT")
FALSE: Token = Token(TokenKind.RAW_ID_LITERAL, "FALSE")
TRUE: Token = Token(TokenKind.RAW_ID_LITERAL, "TRUE")
IDENTITY: Token = Token(TokenKind.RAW_ID, "IDENTITY")

# Keywords
ABORT: Token = Token(TokenKind.KEYWORD, "ABORT")
ACTION: Token = Token(TokenKind.KEYWORD, "ACTION")
ADD: Token = Token(TokenKind.KEYWORD, "ADD")
AFTER: Token = Token(TokenKind.KEYWORD, "AFTER")
ALL: Token = Token(TokenKind.KEYWORD, "ALL")
ALTER: Token = Token(TokenKind.KEYWORD, "ALTER")
ALWAYS: Token = Token(TokenKind.KEYWORD, "ALWAYS")
ANALYZE: Token = Token(TokenKind.KEYWORD, "ANALYZE")
AND: Token = Token(TokenKind.KEYWORD, "AND")
AS: Token = Token(TokenKind.KEYWORD, "AS")
ASC: Token = Token(TokenKind.KEYWORD, "ASC")
ATTACH: Token = Token(TokenKind.KEYWORD, "ATTACH")
AUTOINCREMENT: Token = Token(TokenKind.KEYWORD, "AUTOINCREMENT")
AUTO_INCREMENT: Token = Token(TokenKind.KEYWORD, "AUTO_INCREMENT")
BEFORE: Token = Token(TokenKind.KEYWORD, "BEFORE")
BEGIN: Token = Token(TokenKind.KEYWORD, "BEGIN")
BETWEEN: Token = Token(TokenKind.KEYWORD, "BETWEEN")
BY: Token = Token(TokenKind.KEYWORD, "BY")
CASCADE: Token = Token(TokenKind.KEYWORD, "CASCADE")
CASE: Token = Token(TokenKind.KEYWORD, "CASE")
CAST: Token = Token(TokenKind.KEYWORD, "CAST")
CHECK: Token = Token(TokenKind.KEYWORD, "CHECK")
COLLATE: Token = Token(TokenKind.KEYWORD, "COLLATE")
COLUMN: Token = Token(TokenKind.KEYWORD, "COLUMN")
COMMIT: Token = Token(TokenKind.KEYWORD, "COMMIT")
CONFLICT: Token = Token(TokenKind.KEYWORD, "CONFLICT")
CONSTRAINT: Token = Token(TokenKind.KEYWORD, "CONSTRAINT")
CREATE: Token = Token(TokenKind.KEYWORD, "CREATE")
CROSS: Token = Token(TokenKind.KEYWORD, "CROSS")
CURRENT: Token = Token(TokenKind.KEYWORD, "CURRENT")
CURRENT_DATE: Token = Token(TokenKind.KEYWORD_LITERAL, "CURRENT_DATE")
CURRENT_TIME: Token = Token(TokenKind.KEYWORD_LITERAL, "CURRENT_TIME")
CURRENT_TIMESTAMP: Token = Token(TokenKind.KEYWORD_LITERAL, "CURRENT_TIMESTAMP")
DATABASE: Token = Token(TokenKind.KEYWORD, "DATABASE")
DEFAULT: Token = Token(TokenKind.KEYWORD, "DEFAULT")
DEFERRABLE: Token = Token(TokenKind.KEYWORD, "DEFERRABLE")
DEFERRED: Token = Token(TokenKind.KEYWORD, "DEFERRED")
DELETE: Token = Token(TokenKind.KEYWORD, "DELETE")
DESC: Token = Token(TokenKind.KEYWORD, "DESC")
DETACH: Token = Token(TokenKind.KEYWORD, "DETACH")
DISTINCT: Token = Token(TokenKind.KEYWORD, "DISTINCT")
DO: Token = Token(TokenKind.KEYWORD, "DO")
DROP: Token = Token(TokenKind.KEYWORD, "DROP")
EACH: Token = Token(TokenKind.KEYWORD, "EACH")
ELSE: Token = Token(TokenKind.KEYWORD, "ELSE")
END: Token = Token(TokenKind.KEYWORD, "END")
ESCAPE: Token = Token(TokenKind.KEYWORD, "ESCAPE")
EXCEPT: Token = Token(TokenKind.KEYWORD, "EXCEPT")
EXCLUDE: Token = Token(TokenKind.KEYWORD, "EXCLUDE")
EXCLUSIVE: Token = Token(TokenKind.KEYWORD, "EXCLUSIVE")
EXISTS: Token = Token(TokenKind.KEYWORD, "EXISTS")
EXPLAIN: Token = Token(TokenKind.KEYWORD, "EXPLAIN")
FAIL: Token = Token(TokenKind.KEYWORD, "FAIL")
FILTER: Token = Token(TokenKind.KEYWORD, "FILTER")
FIRST: Token = Token(TokenKind.KEYWORD, "FIRST")
FOLLOWING: Token = Token(TokenKind.KEYWORD, "FOLLOWING")
FOR: Token = Token(TokenKind.KEYWORD, "FOR")
FOREIGN: Token = Token(TokenKind.KEYWORD, "FOREIGN")
FROM: Token = Token(TokenKind.KEYWORD, "FROM")
FULL: Token = Token(TokenKind.KEYWORD, "FULL")
GENERATED: Token = Token(TokenKind.KEYWORD, "GENERATED")
GLOB: Token = Token(TokenKind.KEYWORD, "GLOB")
GROUP: Token = Token(TokenKind.KEYWORD, "GROUP")
GROUPS: Token = Token(TokenKind.KEYWORD, "GROUPS")
HAVING: Token = Token(TokenKind.KEYWORD, "HAVING")
IF: Token = Token(TokenKind.KEYWORD, "IF")
IGNORE: Token = Token(TokenKind.KEYWORD, "IGNORE")
IMMEDIATE: Token = Token(TokenKind.KEYWORD, "IMMEDIATE")
IN: Token = Token(TokenKind.KEYWORD, "IN")
INDEX: Token = Token(TokenKind.KEYWORD, "INDEX")
INDEXED: Token = Token(TokenKind.KEYWORD, "INDEXED")
INITIALLY: Token = Token(TokenKind.KEYWORD, "INITIALLY")
INNER: Token = Token(TokenKind.KEYWORD, "INNER")
INSERT: Token = Token(TokenKind.KEYWORD, "INSERT")
INSTEAD: Token = Token(TokenKind.KEYWORD, "INSTEAD")
INTERSECT: Token = Token(TokenKind.KEYWORD, "INTERSECT")
INTO: Token = Token(TokenKind.KEYWORD, "INTO")
IS: Token = Token(TokenKind.KEYWORD, "IS")
ISNULL: Token = Token(TokenKind.KEYWORD, "ISNULL")
JOIN: Token = Token(TokenKind.KEYWORD, "JOIN")
KEY: Token = Token(TokenKind.KEYWORD, "KEY")
LAST: Token = Token(TokenKind.KEYWORD, "LAST")
LEFT: Token = Token(TokenKind.KEYWORD, "LEFT")
LIKE: Token = Token(TokenKind.KEYWORD, "LIKE")
LIMIT: Token = Token(TokenKind.KEYWORD, "LIMIT")
MATCH: Token = Token(TokenKind.KEYWORD, "MATCH")
MATERIALIZED: Token = Token(TokenKind.KEYWORD, "MATERIALIZED")
NATURAL: Token = Token(TokenKind.KEYWORD, "NATURAL")
NO: Token = Token(TokenKind.KEYWORD, "NO")
NOT: Token = Token(TokenKind.KEYWORD, "NOT")
NOTHING: Token = Token(TokenKind.KEYWORD, "NOTHING")
NOTNULL: Token = Token(TokenKind.KEYWORD, "NOTNULL")
NULL: Token = Token(TokenKind.KEYWORD_LITERAL, "NULL")
NULLS: Token = Token(TokenKind.KEYWORD, "NULLS")
OF: Token = Token(TokenKind.KEYWORD, "OF")
OFFSET: Token = Token(TokenKind.KEYWORD, "OFFSET")
ON: Token = Token(TokenKind.KEYWORD, "ON")
OR: Token = Token(TokenKind.KEYWORD, "OR")
ORDER: Token = Token(TokenKind.KEYWORD, "ORDER")
OTHERS: Token = Token(TokenKind.KEYWORD, "OTHERS")
OUTER: Token = Token(TokenKind.KEYWORD, "OUTER")
OVER: Token = Token(TokenKind.KEYWORD, "OVER")
PARTITION: Token = Token(TokenKind.KEYWORD, "PARTITION")
PLAN: Token = Token(TokenKind.KEYWORD, "PLAN")
PRAGMA: Token = Token(TokenKind.KEYWORD, "PRAGMA")
PRECEDING: Token = Token(TokenKind.KEYWORD, "PRECEDING")
PRIMARY: Token = Token(TokenKind.KEYWORD, "PRIMARY")
QUERY: Token = Token(TokenKind.KEYWORD, "QUERY")
RAISE: Token = Token(TokenKind.KEYWORD, "RAISE")
RANGE: Token = Token(TokenKind.KEYWORD, "RANGE")
RECURSIVE: Token = Token(TokenKind.KEYWORD, "RECURSIVE")
REFERENCES: Token = Token(TokenKind.KEYWORD, "REFERENCES")
REGEXP: Token = Token(TokenKind.KEYWORD, "REGEXP")
REINDEX: Token = Token(TokenKind.KEYWORD, "REINDEX")
RELEASE: Token = Token(TokenKind.KEYWORD, "RELEASE")
RENAME: Token = Token(TokenKind.KEYWORD, "RENAME")
REPLACE: Token = Token(TokenKind.KEYWORD, "REPLACE")
RESTRICT: Token = Token(TokenKind.KEYWORD, "RESTRICT")
RETURNING: Token = Token(TokenKind.KEYWORD, "RETURNING")
RIGHT: Token = Token(TokenKind.KEYWORD, "RIGHT")
ROLLBACK: Token = Token(TokenKind.KEYWORD, "ROLLBACK")
ROW: Token = Token(TokenKind.KEYWORD, "ROW")
ROWS: Token = Token(TokenKind.KEYWORD, "ROWS")
SAVEPOINT: Token = Token(TokenKind.KEYWORD, "SAVEPOINT")
SELECT: Token = Token(TokenKind.KEYWORD, "SELECT")
SET: Token = Token(TokenKind.KEYWORD, "SET")
TABLE: Token = Token(TokenKind.KEYWORD, "TABLE")
TEMP: Token = Token(TokenKind.KEYWORD, "TEMP")
TEMPORARY: Token = Token(TokenKind.KEYWORD, "TEMPORARY")
THEN: Token = Token(TokenKind.KEYWORD, "THEN")
TIES: Token = Token(TokenKind.KEYWORD, "TIES")
TO: Token = Token(TokenKind.KEYWORD, "TO")
TRANSACTION: Token = Token(TokenKind.KEYWORD, "TRANSACTION")
TRIGGER: Token = Token(TokenKind.KEYWORD, "TRIGGER")
UNBOUNDED: Token = Token(TokenKind.KEYWORD, "UNBOUNDED")
UNION: Token = Token(TokenKind.KEYWORD, "UNION")
UNIQUE: Token = Token(TokenKind.KEYWORD, "UNIQUE")
UPDATE: Token = Token(TokenKind.KEYWORD, "UPDATE")
USING: Token = Token(TokenKind.KEYWORD, "USING")
VACUUM: Token = Token(TokenKind.KEYWORD, "VACUUM")
VALUES: Token = Token(TokenKind.KEYWORD, "VALUES")
VIEW: Token = Token(TokenKind.KEYWORD, "VIEW")
VIRTUAL: Token = Token(TokenKind.KEYWORD, "VIRTUAL")
WHEN: Token = Token(TokenKind.KEYWORD, "WHEN")
WHERE: Token = Token(TokenKind.KEYWORD, "WHERE")
WINDOW: Token = Token(TokenKind.KEYWORD, "WINDOW")
WITH: Token = Token(TokenKind.KEYWORD, "WITH")
WITHOUT: Token = Token(TokenKind.KEYWORD, "WITHOUT")

INTERNED: dict[str, Token] = {
    # All operators with two character corresponds to the concatenation of
    # two single-char operators, except operators starting with !
    # To simplify lookup we bind ! with a interned token.
    "!": Token(TokenKind.UNKNOWN, "!"),
    "#": Token(TokenKind.UNKNOWN, "#"),
    # Spaces
    "\n": NEWLINE,
    "\r": Token(TokenKind.WHITESPACE, "\r"),
    " ": Token(TokenKind.WHITESPACE, " "),
    "\t": Token(TokenKind.WHITESPACE, "\t"),
    "\v": Token(TokenKind.WHITESPACE, "\v"),
    "\f": Token(TokenKind.WHITESPACE, "\f"),
    # Binary operators
    "~": BIN_NEG,
    "&": BIN_AND,
    "|": BIN_OR,
    "<<": BIN_LSHIFT,
    ">>": BIN_RSHIFT,
    # Numeric operators
    "+": NUM_PLUS,
    "-": NUM_MINUS,
    "/": NUM_DIV,
    "*": WILDCARD,
    "%": NUM_MOD,
    "^": NUM_EXP,
    # String operators
    "||": STR_CONCAT,
    # Comparison operators
    "=": CMP_EQ,
    "==": CMP_EQ2,
    "<>": CMP_NEQ,
    "<": CMP_LT,
    "<=": CMP_LEQ,
    ">": CMP_GT,
    ">=": CMP_GEQ,
    "!=": CMP_NEQ2,
    "!<": CMP_LEQ2,
    "!>": CMP_GEQ2,
    # Punctuation
    ".": DOT,
    ",": COMMA,
    ":": COLON,
    "::": DOUBLE_COLON,
    ";": SEMICOLON,
    "(": L_PAREN,
    ")": R_PAREN,
    # Known raw identifiers
    "ROWID": ROWID,
    "STRICT": STRICT,
    "FALSE": FALSE,
    "TRUE": TRUE,
    "IDENTITY": IDENTITY,
    # Keywords
    "ABORT": ABORT,
    "ACTION": ACTION,
    "ADD": ADD,
    "AFTER": AFTER,
    "ALL": ALL,
    "ALTER": ALTER,
    "ALWAYS": ALWAYS,
    "ANALYZE": ANALYZE,
    "AND": AND,
    "AS": AS,
    "ASC": ASC,
    "ATTACH": ATTACH,
    "AUTOINCREMENT": AUTOINCREMENT,
    "AUTO_INCREMENT": AUTO_INCREMENT,
    "BEFORE": BEFORE,
    "BEGIN": BEGIN,
    "BETWEEN": BETWEEN,
    "BY": BY,
    "CASCADE": CASCADE,
    "CASE": CASE,
    "CAST": CAST,
    "CHECK": CHECK,
    "COLLATE": COLLATE,
    "COLUMN": COLUMN,
    "COMMIT": COMMIT,
    "CONFLICT": CONFLICT,
    "CONSTRAINT": CONSTRAINT,
    "CREATE": CREATE,
    "CROSS": CROSS,
    "CURRENT": CURRENT,
    "CURRENT_DATE": CURRENT_DATE,
    "CURRENT_TIME": CURRENT_TIME,
    "CURRENT_TIMESTAMP": CURRENT_TIMESTAMP,
    "DATABASE": DATABASE,
    "DEFAULT": DEFAULT,
    "DEFERRABLE": DEFERRABLE,
    "DEFERRED": DEFERRED,
    "DELETE": DELETE,
    "DESC": DESC,
    "DETACH": DETACH,
    "DISTINCT": DISTINCT,
    "DO": DO,
    "DROP": DROP,
    "EACH": EACH,
    "ELSE": ELSE,
    "END": END,
    "ESCAPE": ESCAPE,
    "EXCEPT": EXCEPT,
    "EXCLUDE": EXCLUDE,
    "EXCLUSIVE": EXCLUSIVE,
    "EXISTS": EXISTS,
    "EXPLAIN": EXPLAIN,
    "FAIL": FAIL,
    "FILTER": FILTER,
    "FIRST": FIRST,
    "FOLLOWING": FOLLOWING,
    "FOR": FOR,
    "FOREIGN": FOREIGN,
    "FROM": FROM,
    "FULL": FULL,
    "GENERATED": GENERATED,
    "GLOB": GLOB,
    "GROUP": GROUP,
    "GROUPS": GROUPS,
    "HAVING": HAVING,
    "IF": IF,
    "IGNORE": IGNORE,
    "IMMEDIATE": IMMEDIATE,
    "IN": IN,
    "INDEX": INDEX,
    "INDEXED": INDEXED,
    "INITIALLY": INITIALLY,
    "INNER": INNER,
    "INSERT": INSERT,
    "INSTEAD": INSTEAD,
    "INTERSECT": INTERSECT,
    "INTO": INTO,
    "IS": IS,
    "ISNULL": ISNULL,
    "JOIN": JOIN,
    "KEY": KEY,
    "LAST": LAST,
    "LEFT": LEFT,
    "LIKE": LIKE,
    "LIMIT": LIMIT,
    "MATCH": MATCH,
    "MATERIALIZED": MATERIALIZED,
    "NATURAL": NATURAL,
    "NO": NO,
    "NOT": NOT,
    "NOTHING": NOTHING,
    "NOTNULL": NOTNULL,
    "NULL": NULL,
    "NULLS": NULLS,
    "OF": OF,
    "OFFSET": OFFSET,
    "ON": ON,
    "OR": OR,
    "ORDER": ORDER,
    "OTHERS": OTHERS,
    "OUTER": OUTER,
    "OVER": OVER,
    "PARTITION": PARTITION,
    "PLAN": PLAN,
    "PRAGMA": PRAGMA,
    "PRECEDING": PRECEDING,
    "PRIMARY": PRIMARY,
    "QUERY": QUERY,
    "RAISE": RAISE,
    "RANGE": RANGE,
    "RECURSIVE": RECURSIVE,
    "REFERENCES": REFERENCES,
    "REGEXP": REGEXP,
    "REINDEX": REINDEX,
    "RELEASE": RELEASE,
    "RENAME": RENAME,
    "REPLACE": REPLACE,
    "RESTRICT": RESTRICT,
    "RETURNING": RETURNING,
    "RIGHT": RIGHT,
    "ROLLBACK": ROLLBACK,
    "ROW": ROW,
    "ROWS": ROWS,
    "SAVEPOINT": SAVEPOINT,
    "SELECT": SELECT,
    "SET": SET,
    "TABLE": TABLE,
    "TEMP": TEMP,
    "TEMPORARY": TEMPORARY,
    "THEN": THEN,
    "TIES": TIES,
    "TO": TO,
    "TRANSACTION": TRANSACTION,
    "TRIGGER": TRIGGER,
    "UNBOUNDED": UNBOUNDED,
    "UNION": UNION,
    "UNIQUE": UNIQUE,
    "UPDATE": UPDATE,
    "USING": USING,
    "VACUUM": VACUUM,
    "VALUES": VALUES,
    "VIEW": VIEW,
    "VIRTUAL": VIRTUAL,
    "WHEN": WHEN,
    "WHERE": WHERE,
    "WINDOW": WINDOW,
    "WITH": WITH,
    "WITHOUT": WITHOUT,
}
