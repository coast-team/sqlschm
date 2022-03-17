from dataclasses import dataclass
from typing import Iterator, Iterable, Generic, TypeVar
from sqlschm import tok

T = TypeVar("T")


@dataclass(slots=True)
class ItemCursor(Generic[T]):
    _it: Iterator[T]
    _default_item: T
    item: T
    # Enable to look ahead
    next_item: T

    def __init__(self, items: Iterable[T], default_item: T):
        self._it = iter(items)
        self._default_item = default_item
        self.next_item = default_item
        self.forth()
        self.forth()

    def forth(self) -> None:
        self.item = self.next_item
        self.next_item = next(self._it, self._default_item)


def tokens(src: Iterable[str], /) -> Iterable[tok.Token]:
    cs = ItemCursor(src, None)
    while cs.item is not None:
        assert len(cs.item) == 1
        if cs.item.isspace():
            yield tok.INTERNED[cs.item]
            cs.forth()
        elif cs.item.isdecimal() or (
            cs.item == "." and cs.next_item is not None and cs.next_item.isdecimal()
        ):
            yield _numeric_token(cs)
        elif cs.item.isidentifier():
            id = _identifier(cs)
            id_upper = id.upper()
            if id_upper == "B" and cs.item in ["'", '"']:
                yield _bin_token(cs)
            elif id_upper == "X" and cs.item in ["'", '"']:
                yield _blob_token(cs)
            elif id_upper in tok.INTERNED:
                yield tok.INTERNED[id_upper]
            else:
                yield tok.Token(tok.TokenKind.RAW_ID, id)
        elif cs.item in "'\"":
            yield _str_token(cs)
        elif cs.item in "`[":
            yield _enclosed_id_token(cs)
        elif cs.item in tok.INTERNED:
            concat = cs.item + cs.next_item if cs.next_item is not None else cs.item
            if concat == "--" or concat == "# ":
                yield _single_line_comment_token(cs)
            elif concat == "/*":
                yield _multi_line_comment_token(cs)
            else:
                if concat in tok.INTERNED:
                    yield tok.INTERNED[concat]
                    cs.forth()
                else:
                    yield tok.INTERNED[cs.item]
                cs.forth()
        else:
            yield tok.Token(tok.TokenKind.UNKNOWN, cs.item)
            cs.forth()


def _single_line_comment_token(cs: ItemCursor[str | None], /) -> tok.Token:
    cs.forth()  # consume -
    cs.forth()  # consume -
    content = ""
    while cs.item is not None and cs.item != "\n":
        content += cs.item
        cs.forth()
    cs.forth()  # consume  \n or None
    return tok.Token(tok.TokenKind.SINGLE_LINE_COMMENT, content)


def _multi_line_comment_token(cs: ItemCursor[str | None], /) -> tok.Token:
    cs.forth()  # consume /
    cs.forth()  # consume *
    content = ""
    while (
        cs.item is not None
        and cs.next_item is not None
        and (cs.item + cs.next_item) != "*/"
    ):
        content += cs.item
        cs.forth()
    if cs.item is None or cs.next_item is None:
        if cs.item is not None:
            content += cs.item
            cs.forth()
        return tok.Token(tok.TokenKind.UNKNOWN, f"/*{content}")
    cs.forth()  # consume *
    cs.forth()  # consume /
    return tok.Token(tok.TokenKind.MULTI_LINE_COMMENT, content)


def _blob_token(cs: ItemCursor[str | None], /) -> tok.Token:
    assert cs.item in ["'", '"']
    delim = cs.item
    cs.forth()  # consume ' or "
    n = _hex_literal(cs)
    if cs.item != delim:
        return tok.Token(tok.TokenKind.UNKNOWN, f"{delim}{n}")
    cs.forth()  # consume ' or "
    return tok.Token(tok.TokenKind.BLOB, n)


def _bin_token(cs: ItemCursor[str | None], /) -> tok.Token:
    assert cs.item in ["'", '"']
    delim = cs.item
    cs.forth()  # consume ' or "
    n = _bin_literal(cs)
    if cs.item != delim:
        return tok.Token(tok.TokenKind.UNKNOWN, f"{delim}{n}")
    cs.forth()  # consume ' or "
    return tok.Token(tok.TokenKind.BINARY, n)


def _numeric_token(cs: ItemCursor[str | None], /) -> tok.Token:
    first_part = _fractional_literal(cs)
    if "e" in first_part:
        return tok.Token(tok.TokenKind.FLOAT, first_part)
    if cs.item == ".":
        cs.forth()
        val = first_part + "." + _fractional_literal(cs)
        return tok.Token(tok.TokenKind.FLOAT, val)
    elif first_part == "0" and cs.item in ["x", "X"]:
        x = cs.item
        cs.forth()
        if cs.item in _HEX_DIGITS:
            return tok.Token(tok.TokenKind.HEX, _hex_literal(cs))
        else:
            return tok.Token(tok.TokenKind.UNKNOWN, f"0{x}")
    return tok.Token(tok.TokenKind.INT, first_part)


def _str_token(cs: ItemCursor[str | None], /) -> tok.Token:
    assert cs.item is not None
    delim = cs.item  # " or '
    cs.forth()  # consume delim
    s = ""
    while cs.item is not None and (cs.item != delim or cs.next_item == delim):
        # escaped delim?
        if cs.item == delim:
            assert cs.next_item == delim
            cs.forth()
        s += cs.item
        cs.forth()
    if cs.item is None:
        return tok.Token(tok.TokenKind.UNKNOWN, f"{delim}{s}")
    cs.forth()  # consume delim
    kind = tok.TokenKind.STD_STR if delim == "'" else tok.TokenKind.STD_DELIMITED_ID
    return tok.Token(kind, s)


def _enclosed_id_token(cs: ItemCursor[str | None], /) -> tok.Token:
    delim = cs.item
    cs.forth()
    s = _identifier(cs)
    if cs.item != delim:
        pass
    cs.forth()
    return tok.Token(tok.TokenKind.NON_STD_DELIMITED_ID, s)


def _identifier(cs: ItemCursor[str | None], /) -> str:
    result: str = ""
    while cs.item is not None and (cs.item in "_$" or cs.item.isalnum()):
        result += cs.item
        cs.forth()
    return result


def _fractional_literal(cs: ItemCursor[str | None], /) -> str:
    decimal = _int_literal(cs)
    if cs.item in ["e", "E"]:
        cs.forth()
        sign = ""
        if cs.item in ["+", "-"]:
            sign = cs.item
            cs.forth()
        exponent = _int_literal(cs)
        return decimal + "e" + sign + exponent
    return decimal


def _hex_literal(cs: ItemCursor[str | None], /) -> str:
    result: str = ""
    while cs.item in _HEX_DIGITS:
        result += cs.item
        cs.forth()
    return result


def _bin_literal(cs: ItemCursor[str | None], /) -> str:
    result: str = ""
    while cs.item in ["0", "1"]:
        result += cs.item
        cs.forth()
    return result


def _int_literal(cs: ItemCursor[str | None], /) -> str:
    result: str = ""
    while cs.item is not None and cs.item.isdecimal():
        result += cs.item
        cs.forth()
    return result


_HEX_DIGITS: frozenset[str] = frozenset(iter("0123456789ABCDEFabcdef"))
