from sqlschm import sql, parser

TABLE_A = sql.Table(
    name=("A",),
    columns=(sql.Column(name="a"),),
    constraints=(sql.Uniqueness(indexed=(sql.Indexed(column="a"),), is_primary=True),),
)
TABLE_B = sql.Table(
    name=("B",),
    columns=(sql.Column(name="b"),),
    constraints=(sql.Uniqueness(indexed=(sql.Indexed(column="b"),), is_primary=True),),
)
FK_A = sql.ForeignKey(columns=("a",), foreign_table=("A",), referred_columns=("a",))
FK_B = sql.ForeignKey(columns=("b",), foreign_table=("B",))
TABLE_C = sql.Table(
    name=("C",),
    columns=(sql.Column(name="a"), sql.Column(name="b")),
    constraints=(
        sql.Uniqueness(
            indexed=(sql.Indexed(column="a"), sql.Indexed(column="b")), is_primary=True
        ),
        FK_A,
        FK_B,
    ),
)
FK_C = sql.ForeignKey(
    columns=("x", "y"),
    foreign_table=("C",),
    referred_columns=("b", "a"),
)
TABLE_D = sql.Table(
    name=("D",),
    columns=(sql.Column(name="x"), sql.Column(name="y")),
    constraints=(
        sql.Uniqueness(
            indexed=(sql.Indexed(column="x"), sql.Indexed(column="y")), is_primary=True
        ),
        FK_C,
    ),
)
SYMBOLS = {
    "A": TABLE_A,
    "B": TABLE_B,
    "C": TABLE_C,
    "D": TABLE_D,
}
SCHEMA = sql.Schema(items=(TABLE_A, TABLE_B, TABLE_C, TABLE_D))


def test_symbols() -> None:
    assert sql.symbols(SCHEMA) == SYMBOLS


def test_referred_columns() -> None:
    assert sql.referred_columns(FK_A, SYMBOLS) == ("a",)
    assert sql.referred_columns(FK_B, SYMBOLS) == ("b",)
    assert sql.referred_columns(FK_C, SYMBOLS) == ("b", "a")


def test_resolve_foreign_key() -> None:
    assert tuple(sql.resolve_foreign_key(FK_A, "a", SYMBOLS)) == ("a",)
    assert tuple(sql.resolve_foreign_key(FK_B, "b", SYMBOLS)) == ("b",)
    assert tuple(sql.resolve_foreign_key(FK_C, "x", SYMBOLS)) == (
        FK_B,
        "b",
    )
    assert tuple(sql.resolve_foreign_key(FK_C, "y", SYMBOLS)) == (
        FK_A,
        "a",
    )
