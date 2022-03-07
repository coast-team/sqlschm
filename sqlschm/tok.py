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
NEWLINE = Token(TokenKind.WHITESPACE, "\n")

# *
WILDCARD = Token(TokenKind.NUM_OP, "*")

# Binary operators
BIN_NEG = Token(TokenKind.BIN_OP, "~")
BIN_AND = Token(TokenKind.BIN_OP, "&")
BIN_OR = Token(TokenKind.BIN_OP, "|")
BIN_LSHIFT = Token(TokenKind.BIN_OP, "<<")
BIN_RSHIFT = Token(TokenKind.BIN_OP, ">>")

# Numeric operators
NUM_PLUS = Token(TokenKind.NUM_OP, "+")
NUM_MINUS = Token(TokenKind.NUM_OP, "-")
NUM_DIV = Token(TokenKind.NUM_OP, "/")
NUM_MOD = Token(TokenKind.NUM_OP, "%")
NUM_EXP = Token(TokenKind.NUM_OP, "^")

# Comparison operators
CMP_EQ = Token(TokenKind.CMP_OP, "=")
CMP_EQ2 = Token(TokenKind.CMP_OP, "==")
CMP_GEQ = Token(TokenKind.CMP_OP, ">=")
CMP_GEQ2 = Token(TokenKind.CMP_OP, "!>")
CMP_GT = Token(TokenKind.CMP_OP, ">")
CMP_LEQ = Token(TokenKind.CMP_OP, "<=")
CMP_LEQ2 = Token(TokenKind.CMP_OP, "!<")
CMP_LT = Token(TokenKind.CMP_OP, "<")
CMP_NEQ = Token(TokenKind.CMP_OP, "<>")
CMP_NEQ2 = Token(TokenKind.CMP_OP, "!=")

# String operators
STR_CONCAT = Token(TokenKind.STR_OP, "||")

# Punctuation
DOT = Token(TokenKind.PUNCTUATION, ".")
COMMA = Token(TokenKind.PUNCTUATION, ",")
COLON = Token(TokenKind.PUNCTUATION, ":")
DOUBLE_COLON = Token(TokenKind.PUNCTUATION, "::")
SEMICOLON = Token(TokenKind.PUNCTUATION, ";")
L_PAREN = Token(TokenKind.PUNCTUATION, "(")
R_PAREN = Token(TokenKind.PUNCTUATION, ")")

# Known raw identifiers
ROWID = Token(TokenKind.RAW_ID, "ROWID")
STRICT = Token(TokenKind.RAW_ID, "STRICT")
FALSE = Token(TokenKind.RAW_ID_LITERAL, "FALSE")
TRUE = Token(TokenKind.RAW_ID_LITERAL, "TRUE")
IDENTITY = Token(TokenKind.RAW_ID, "IDENTITY")

# Keywords
ABORT = Token(TokenKind.KEYWORD, "ABORT")
ACTION = Token(TokenKind.KEYWORD, "ACTION")
ADD = Token(TokenKind.KEYWORD, "ADD")
AFTER = Token(TokenKind.KEYWORD, "AFTER")
ALL = Token(TokenKind.KEYWORD, "ALL")
ALTER = Token(TokenKind.KEYWORD, "ALTER")
ALWAYS = Token(TokenKind.KEYWORD, "ALWAYS")
ANALYZE = Token(TokenKind.KEYWORD, "ANALYZE")
AND = Token(TokenKind.KEYWORD, "AND")
AS = Token(TokenKind.KEYWORD, "AS")
ASC = Token(TokenKind.KEYWORD, "ASC")
ATTACH = Token(TokenKind.KEYWORD, "ATTACH")
AUTOINCREMENT = Token(TokenKind.KEYWORD, "AUTOINCREMENT")
AUTO_INCREMENT = Token(TokenKind.KEYWORD, "AUTO_INCREMENT")
BEFORE = Token(TokenKind.KEYWORD, "BEFORE")
BEGIN = Token(TokenKind.KEYWORD, "BEGIN")
BETWEEN = Token(TokenKind.KEYWORD, "BETWEEN")
BY = Token(TokenKind.KEYWORD, "BY")
CASCADE = Token(TokenKind.KEYWORD, "CASCADE")
CASE = Token(TokenKind.KEYWORD, "CASE")
CAST = Token(TokenKind.KEYWORD, "CAST")
CHECK = Token(TokenKind.KEYWORD, "CHECK")
COLLATE = Token(TokenKind.KEYWORD, "COLLATE")
COLUMN = Token(TokenKind.KEYWORD, "COLUMN")
COMMIT = Token(TokenKind.KEYWORD, "COMMIT")
CONFLICT = Token(TokenKind.KEYWORD, "CONFLICT")
CONSTRAINT = Token(TokenKind.KEYWORD, "CONSTRAINT")
CREATE = Token(TokenKind.KEYWORD, "CREATE")
CROSS = Token(TokenKind.KEYWORD, "CROSS")
CURRENT = Token(TokenKind.KEYWORD, "CURRENT")
CURRENT_DATE = Token(TokenKind.KEYWORD_LITERAL, "CURRENT_DATE")
CURRENT_TIME = Token(TokenKind.KEYWORD_LITERAL, "CURRENT_TIME")
CURRENT_TIMESTAMP = Token(TokenKind.KEYWORD_LITERAL, "CURRENT_TIMESTAMP")
DATABASE = Token(TokenKind.KEYWORD, "DATABASE")
DEFAULT = Token(TokenKind.KEYWORD, "DEFAULT")
DEFERRABLE = Token(TokenKind.KEYWORD, "DEFERRABLE")
DEFERRED = Token(TokenKind.KEYWORD, "DEFERRED")
DELETE = Token(TokenKind.KEYWORD, "DELETE")
DESC = Token(TokenKind.KEYWORD, "DESC")
DETACH = Token(TokenKind.KEYWORD, "DETACH")
DISTINCT = Token(TokenKind.KEYWORD, "DISTINCT")
DO = Token(TokenKind.KEYWORD, "DO")
DROP = Token(TokenKind.KEYWORD, "DROP")
EACH = Token(TokenKind.KEYWORD, "EACH")
ELSE = Token(TokenKind.KEYWORD, "ELSE")
END = Token(TokenKind.KEYWORD, "END")
ESCAPE = Token(TokenKind.KEYWORD, "ESCAPE")
EXCEPT = Token(TokenKind.KEYWORD, "EXCEPT")
EXCLUDE = Token(TokenKind.KEYWORD, "EXCLUDE")
EXCLUSIVE = Token(TokenKind.KEYWORD, "EXCLUSIVE")
EXISTS = Token(TokenKind.KEYWORD, "EXISTS")
EXPLAIN = Token(TokenKind.KEYWORD, "EXPLAIN")
FAIL = Token(TokenKind.KEYWORD, "FAIL")
FILTER = Token(TokenKind.KEYWORD, "FILTER")
FIRST = Token(TokenKind.KEYWORD, "FIRST")
FOLLOWING = Token(TokenKind.KEYWORD, "FOLLOWING")
FOR = Token(TokenKind.KEYWORD, "FOR")
FOREIGN = Token(TokenKind.KEYWORD, "FOREIGN")
FROM = Token(TokenKind.KEYWORD, "FROM")
FULL = Token(TokenKind.KEYWORD, "FULL")
GENERATED = Token(TokenKind.KEYWORD, "GENERATED")
GLOB = Token(TokenKind.KEYWORD, "GLOB")
GROUP = Token(TokenKind.KEYWORD, "GROUP")
GROUPS = Token(TokenKind.KEYWORD, "GROUPS")
HAVING = Token(TokenKind.KEYWORD, "HAVING")
IF = Token(TokenKind.KEYWORD, "IF")
IGNORE = Token(TokenKind.KEYWORD, "IGNORE")
IMMEDIATE = Token(TokenKind.KEYWORD, "IMMEDIATE")
IN = Token(TokenKind.KEYWORD, "IN")
INDEX = Token(TokenKind.KEYWORD, "INDEX")
INDEXED = Token(TokenKind.KEYWORD, "INDEXED")
INITIALLY = Token(TokenKind.KEYWORD, "INITIALLY")
INNER = Token(TokenKind.KEYWORD, "INNER")
INSERT = Token(TokenKind.KEYWORD, "INSERT")
INSTEAD = Token(TokenKind.KEYWORD, "INSTEAD")
INTERSECT = Token(TokenKind.KEYWORD, "INTERSECT")
INTO = Token(TokenKind.KEYWORD, "INTO")
IS = Token(TokenKind.KEYWORD, "IS")
ISNULL = Token(TokenKind.KEYWORD, "ISNULL")
JOIN = Token(TokenKind.KEYWORD, "JOIN")
KEY = Token(TokenKind.KEYWORD, "KEY")
LAST = Token(TokenKind.KEYWORD, "LAST")
LEFT = Token(TokenKind.KEYWORD, "LEFT")
LIKE = Token(TokenKind.KEYWORD, "LIKE")
LIMIT = Token(TokenKind.KEYWORD, "LIMIT")
MATCH = Token(TokenKind.KEYWORD, "MATCH")
MATERIALIZED = Token(TokenKind.KEYWORD, "MATERIALIZED")
NATURAL = Token(TokenKind.KEYWORD, "NATURAL")
NO = Token(TokenKind.KEYWORD, "NO")
NOT = Token(TokenKind.KEYWORD, "NOT")
NOTHING = Token(TokenKind.KEYWORD, "NOTHING")
NOTNULL = Token(TokenKind.KEYWORD, "NOTNULL")
NULL = Token(TokenKind.KEYWORD_LITERAL, "NULL")
NULLS = Token(TokenKind.KEYWORD, "NULLS")
OF = Token(TokenKind.KEYWORD, "OF")
OFFSET = Token(TokenKind.KEYWORD, "OFFSET")
ON = Token(TokenKind.KEYWORD, "ON")
OR = Token(TokenKind.KEYWORD, "OR")
ORDER = Token(TokenKind.KEYWORD, "ORDER")
OTHERS = Token(TokenKind.KEYWORD, "OTHERS")
OUTER = Token(TokenKind.KEYWORD, "OUTER")
OVER = Token(TokenKind.KEYWORD, "OVER")
PARTITION = Token(TokenKind.KEYWORD, "PARTITION")
PLAN = Token(TokenKind.KEYWORD, "PLAN")
PRAGMA = Token(TokenKind.KEYWORD, "PRAGMA")
PRECEDING = Token(TokenKind.KEYWORD, "PRECEDING")
PRIMARY = Token(TokenKind.KEYWORD, "PRIMARY")
QUERY = Token(TokenKind.KEYWORD, "QUERY")
RAISE = Token(TokenKind.KEYWORD, "RAISE")
RANGE = Token(TokenKind.KEYWORD, "RANGE")
RECURSIVE = Token(TokenKind.KEYWORD, "RECURSIVE")
REFERENCES = Token(TokenKind.KEYWORD, "REFERENCES")
REGEXP = Token(TokenKind.KEYWORD, "REGEXP")
REINDEX = Token(TokenKind.KEYWORD, "REINDEX")
RELEASE = Token(TokenKind.KEYWORD, "RELEASE")
RENAME = Token(TokenKind.KEYWORD, "RENAME")
REPLACE = Token(TokenKind.KEYWORD, "REPLACE")
RESTRICT = Token(TokenKind.KEYWORD, "RESTRICT")
RETURNING = Token(TokenKind.KEYWORD, "RETURNING")
RIGHT = Token(TokenKind.KEYWORD, "RIGHT")
ROLLBACK = Token(TokenKind.KEYWORD, "ROLLBACK")
ROW = Token(TokenKind.KEYWORD, "ROW")
ROWS = Token(TokenKind.KEYWORD, "ROWS")
SAVEPOINT = Token(TokenKind.KEYWORD, "SAVEPOINT")
SELECT = Token(TokenKind.KEYWORD, "SELECT")
SET = Token(TokenKind.KEYWORD, "SET")
TABLE = Token(TokenKind.KEYWORD, "TABLE")
TEMP = Token(TokenKind.KEYWORD, "TEMP")
TEMPORARY = Token(TokenKind.KEYWORD, "TEMPORARY")
THEN = Token(TokenKind.KEYWORD, "THEN")
TIES = Token(TokenKind.KEYWORD, "TIES")
TO = Token(TokenKind.KEYWORD, "TO")
TRANSACTION = Token(TokenKind.KEYWORD, "TRANSACTION")
TRIGGER = Token(TokenKind.KEYWORD, "TRIGGER")
UNBOUNDED = Token(TokenKind.KEYWORD, "UNBOUNDED")
UNION = Token(TokenKind.KEYWORD, "UNION")
UNIQUE = Token(TokenKind.KEYWORD, "UNIQUE")
UPDATE = Token(TokenKind.KEYWORD, "UPDATE")
USING = Token(TokenKind.KEYWORD, "USING")
VACUUM = Token(TokenKind.KEYWORD, "VACUUM")
VALUES = Token(TokenKind.KEYWORD, "VALUES")
VIEW = Token(TokenKind.KEYWORD, "VIEW")
VIRTUAL = Token(TokenKind.KEYWORD, "VIRTUAL")
WHEN = Token(TokenKind.KEYWORD, "WHEN")
WHERE = Token(TokenKind.KEYWORD, "WHERE")
WINDOW = Token(TokenKind.KEYWORD, "WINDOW")
WITH = Token(TokenKind.KEYWORD, "WITH")
WITHOUT = Token(TokenKind.KEYWORD, "WITHOUT")

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
